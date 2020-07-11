from __future__ import annotations
from web import db
from sqlalchemy.sql import func

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    attack_id = db.Column(db.Integer, db.ForeignKey('attack.id'))
    attack = db.relationship('Attack')

    # Result is either from `gold` or from a team
    gold = db.Column(db.Boolean())
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team')

    commit_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(), server_default=func.now())
    passed = db.Column(db.Boolean())

    stdout = db.Column(db.Text())
    stdout_hash = db.Column(db.String(64))
    stdout_correct = db.Column(db.Boolean())

    stderr = db.Column(db.Text())
    stderr_hash = db.Column(db.String(64))
    stderr_correct = db.Column(db.Boolean())

    filesystem_hash = db.Column(db.String(64))
    filesystem_correct = db.Column(db.Boolean())

    return_code = db.Column(db.Integer())
    return_code_correct = db.Column(db.Boolean())

    seconds_to_complete = db.Column(db.Float())

    # Contains custom output, such as compilation errors
    output = db.Column(db.Text())

    @property
    def correct_result(self) -> Result:
        return self.attack.gold_result
