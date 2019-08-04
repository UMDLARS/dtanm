from web import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    members = db.relationship('User', back_populates="team")
    results = db.relationship('Result', back_populates="team")
    attacks = db.relationship('Attack', back_populates="team")

    last_commit = db.column(db.String(255))

    most_passing = db.column(db.String(255)) # "87/100"
