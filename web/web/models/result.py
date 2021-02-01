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
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    submitted_by = db.relationship('User')

    commit_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(), server_default=func.now())
    passed = db.Column(db.Boolean())

    notes = db.Column(db.Text) # Used for test-against-gold

    # psycopg2 returns memoryview objects, unless it's zero length, in which
    # case it returns b'', of type bytes. To keep this consistent, we explicitly
    # cast to bytes here.
    _stdout = db.Column("stdout", db.LargeBinary())
    @property
    def stdout(self):
        return bytes(self._stdout)
    stdout_hash = db.Column(db.String(64))
    stdout_correct = db.Column(db.Boolean())

    _stderr = db.Column("stderr", db.LargeBinary())
    @property
    def stderr(self):
        return bytes(self._stderr)
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
