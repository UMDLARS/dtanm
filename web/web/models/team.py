from web import db
from sqlalchemy.sql import text
from web.models.result import Result
from datetime import datetime
from urllib.parse import urlparse
from flask import request

import os
import shutil
import dulwich.porcelain as git
from dulwich.repo import Repo


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255))

    members = db.relationship('User', back_populates="team")
    attacks = db.relationship('Attack', back_populates="team")

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
    def results(self):
        return db.session.query(Result).from_statement(
            text("""WITH results AS (
                SELECT r.*, ROW_NUMBER() OVER (PARTITION BY attack_id ORDER BY created_at DESC) AS rn
                FROM result as r WHERE team_id = :team_id
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
    def last_code_submitted(self):
        r = Repo(f'/cctf/repos/{self.id}')
        HEAD = r.get_object(r.head())
        return datetime.fromtimestamp(HEAD.commit_time)

    @property
    def last_code_hash(self):
        r = Repo(f'/cctf/repos/{self.id}')
        HEAD = r.get_object(r.head())
        return HEAD.id.decode()

    most_passing = db.Column(db.String(255)) # "87/100"
