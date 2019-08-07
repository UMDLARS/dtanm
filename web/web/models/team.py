from web import db
from sqlalchemy.sql import text
from web.models.result import Result

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


    last_commit = db.Column(db.String(255))

    most_passing = db.Column(db.String(255)) # "87/100"
