"""SQLAlchemy models."""
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(10), unique=True)
    synapse_user_id = db.Column(db.String(20), unique=True)

    def __init__(self, slack_user_id, synapse_user_id):
        self.slack_user_id = slack_user_id
        self.synapse_user_id = synapse_user_id

    def __repr__(self):
        return '<User slack: %r, synapse: %r>' % (self.slack_user_id,
                                                  self.synapse_user_id)
