from web import db

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    attack_id = db.Column(db.Integer, db.ForeignKey('attack.id'))
    attack = db.relationship('Attack', back_populates="results")

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', back_populates="results")

    commit_hash = db.column(db.String(255))
    created_at = db.Column(db.DateTime())
    passed = db.Column(db.Boolean())
    output = db.Column(db.Text())
