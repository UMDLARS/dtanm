from web import db
from sqlalchemy.sql import text
from datetime import datetime
from urllib.parse import urlparse
from flask import request
from web.models.task import add_team_score_task
from web import redis
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy import select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, aliased
from sqlalchemy.sql.expression import or_
from datetime import datetime
from typing import List, TYPE_CHECKING
import time

from web import app

import os
import shutil
import dulwich.porcelain as git
from dulwich.repo import Repo

if TYPE_CHECKING:
    from web.models.attack import Attack
    from web.models.result import Result
    from web.models.security import User

class Team(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255))

    members: Mapped[List['User']] = relationship(back_populates="team")
    attacks: Mapped[List['Attack']] = relationship(back_populates="team")
    results: Mapped[List['Result']] = relationship(back_populates="team", cascade="all, delete")
    badges: Mapped[List['Badge']] = relationship(back_populates="team")

    base_score: Mapped[int] = mapped_column()

    # Create folders and repositories for teams
    def set_up_repo(self):
        # Create git repository for team, and add initial files
        repo_dir = os.path.join('/cctf/repos', str(self.id))
        shutil.copytree('/cctf/pack/src', repo_dir)
        os.chdir(repo_dir)
        repo = Repo.init(repo_dir) # Note not init_bare, as we need to add the files. 
        git.add(repo=repo) # Without files specified, defaults to all

        author=f"DTANM Admin <admin@{urlparse(request.base_url).hostname}>"
        git.commit(repo=repo, message="Initial Commit", author=author)

        # Allow pushes to repository.
        # This would normally be done with Dulwich but isn't yet implemented in their library
        # (Currently https://github.com/dulwich/dulwich/blob/debcedf952629e77cd66d1fa0cce1e5079abaa97/dulwich/config.py#L156)
        # using init_bare would solve this problem, if we could use it (see above)
        with open(os.path.join('/cctf/repos/', str(self.id), '.git/config'), "a") as config:
            config.write("[receive]\n\tdenyCurrentBranch = ignore\n")

    @property
    def member_names(self):
        from web.models.security import User
        return [member.name for member in self.members]

    # This massive expression is needed because the db holds all results 
    # for all past tests; results are never deleted.
    # This grabs the latest results against each attack for a team.
    def _get_results(self, passing):
        from web.models.result import Result

        by_created_time = (
            select(
                Result,
                func.row_number()
                    .over(partition_by=Result.attack_id, order_by=Result.created_at.desc())
                    .label("rn")
            )
            .where(Result.team_id == self.id)
            .cte()
        )
        stmt = (
            select(aliased(Result, by_created_time))
            .where(by_created_time.c.rn == 1)
            .where(by_created_time.c.passed == passing)
        )

        return db.session.scalars(stmt).all()

    @property
    def current_result(self):
        from web.models.result import Result

        by_created_time = (
            select(
                Result,
                func.row_number()
                    .over(partition_by=Result.attack_id, order_by=Result.created_at.desc())
                    .label("rn")
            )
            .where(Result.team_id == self.id)
            .cte()
        )
        stmt = (
            select(aliased(Result, by_created_time))
            .where(by_created_time.c.rn == 1)
        )

        return db.session.scalars(stmt).all()

    @property
    def passing(self):
        from web.models.result import Result
        return self._get_results(True)

    @property
    def failing(self):
        from web.models.result import Result
        return self._get_results(False)

    @property
    def last_code_submitted(self):
        r = Repo(f'/cctf/repos/{self.id}')
        HEAD = r.get_object(r.head())
        return datetime.fromtimestamp(HEAD.commit_time)

    @property
    def last_code_hash(self):
        r = Repo(f'/cctf/repos/{self.id}')
        HEAD = r.get_object(r.head())
        return HEAD.id.decode()

    def rescore_all_attacks(self):
        from web.models.attack import Attack
        for attack in Attack.query.all():
            add_team_score_task(self.id, attack.id)

    @property
    def is_being_scored(self):
        for task in redis.zrange('tasks', '0', '-1'):
            if task.decode().startswith(str(self.id) + '-'):
                return True
        return False

    @property
    def badge_list(self):
        """
        Returns a list of simple badge objects, rather than the query results,
        which include relationships and cannot be simply serialized with
        JSON.dumps() or Jinja's tojson filter.
        """
        return [{"id": badge.id, "type": badge.type, "content": badge.content, "team_id": badge.team_id} for badge in self.badges]

    @property
    def score(self):
        from web.models.result import Result
        from web.models.attack import Attack

        # Periodic attack points aren't added to base scores until an attack is fixed
        # by a team, so we need to compute that part on the fly.
        # Could this be done better, probably.
        # Does it work, yes :)
        try:
            # This first part gives the sums of all current first_failed_at times

            # Grab the most current results
            by_created_time = (
                select(
                    Result.first_failed_at,
                    Result.passed,
                    func.row_number()
                        .over(partition_by=Result.attack_id, order_by=Result.created_at.desc())
                        .label("rn")
                )
                .where(Result.team_id != self.id)
                .where(Attack.team_id == self.id)
                .outerjoin(Attack)
                .cte('by_created')
            )
            # Sum and count the failed results
            sum_stmt = (
                select(
                    func.sum(by_created_time.c.first_failed_at).label("times"),
                    func.count(by_created_time.c.first_failed_at).label("num"),
                )
                .where(by_created_time.c.rn == 1)
                .where(by_created_time.c.passed == False)
                .add_cte(by_created_time)
                .cte('filter_rn1')
            )
            # Tack on the team's base score
            stmt = (
                select(
                    sum_stmt.c.times,
                    sum_stmt.c.num,
                    Team.base_score # lol
                )
                .where(Team.id == self.id)
                .add_cte(sum_stmt)
            )

            #app.logger.error(stmt)

            result = db.session.execute(stmt).first()
            #app.logger.error(f'r = {result.times}, {result.num}, {result.base_score}')

            if result.num > 0:
                # Compute the cumulative time diff.
                diff = (result.num * time.time()) - result.times

                # Compute the total score.
                interval = app.config['PERIODIC_ATTACK_UPDATE_INTERVAL']
                inc = app.config['PERIODIC_ATTACK_SCORE_INC']

                return result.base_score + diff / interval * inc

            # No failed results, just return the base score.
            return result.base_score
        except Exception as e:
            app.logger.exception(e)
        
        return -1

class Badge(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    team_id: Mapped[int] = mapped_column(ForeignKey('team.id'))
    team: Mapped['Team'] = relationship()

    type: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(255))
