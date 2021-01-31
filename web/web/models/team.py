from web import db
from sqlalchemy.sql import text
from web.models.result import Result
from datetime import datetime
from urllib.parse import urlparse
from flask import request
from web.models.task import add_task
from web.models.attack import Attack
from web import redis

import os
import shutil
import dulwich.porcelain as git
from dulwich.repo import Repo


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255))

    members = db.relationship('User', back_populates="team")
    attacks = db.relationship('Attack', back_populates="team")
    badges = db.relationship('Badge', back_populates="team")

    # Create folders and repositories for teams
    def set_up_repo(self):
        # Create git repository for team, and add initial files
        repo_dir = os.path.join('/cctf/repos', str(self.id))
        shutil.copytree('/pack/src', repo_dir)
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
        return [member.name for member in self.members]

    @property
    def results(self):
        return db.session.query(Result).from_statement(
            text("""
                WITH results AS (
                    SELECT r.*, ROW_NUMBER() OVER (PARTITION BY r.attack_id ORDER BY r.created_at DESC) AS rn
                    FROM result r INNER JOIN attack a ON r.attack_id = a.id WHERE a.team_id = :team_id AND a.type = 'attack'
                ) SELECT * from results WHERE rn = 1;
                """)
        ).params(team_id=self.id).all()

    @property
    def passing(self):
        return [r for r in self.results if r.passed]

    @property
    def failing(self):
        return [r for r in self.results if not r.passed]

    @property
    def tests_against_gold(self):
        return Result.query.join(Attack).filter(Result.team_id == self.id, Attack.type == "test").all()

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
        for attack in Attack.query.filter(Attack.type == "attack").all():
            add_task(self.id, attack.id)

    @property
    def is_being_scored(self):
        for task in redis.zrange('tasks', '0', '-1'):
            if task.decode().startswith(str(self.id) + '-'):
                return True
        return False

    most_passing = db.Column(db.String(255)) # "87/100"

    @property
    def badge_list(self):
        """
        Returns a list of simple badge objects, rather than the query results,
        which include relationships and cannot be simply serialized with
        JSON.dumps() or Jinja's tojson filter.
        """
        return [{"id": badge.id, "type": badge.type, "content": badge.content, "team_id": badge.team_id} for badge in self.badges]


class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team')

    type = db.Column(db.String(255))
    content = db.Column(db.String(255))
