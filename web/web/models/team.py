from web import db
from sqlalchemy.sql import text
from web.models.result import Result
from dulwich.repo import Repo
from datetime import datetime

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255))

    members = db.relationship('User', back_populates="team")
    attacks = db.relationship('Attack', back_populates="team")

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
