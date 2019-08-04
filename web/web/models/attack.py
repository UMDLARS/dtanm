from web import db

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255))

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', back_populates="attacks")

    results = db.relationship('Result', back_populates="attack")

    created_at = db.Column(db.DateTime())
    location = db.Column(db.String(255))
