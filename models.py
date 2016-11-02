"""SQLAlchemy models."""
from db_config import db


class User(db.Model):
    """Store slack user id and synapse user id.

    Todo:
        - Index slack_user_id
    """
    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(15))  # TODO: (after testing) unique=True
    synapse_user_id = db.Column(db.String(30))  # TODO: (after testing) unique=True

    def __init__(self, slack_user_id, synapse_user_id):
        self.slack_user_id = slack_user_id
        self.synapse_user_id = synapse_user_id

    def __repr__(self):
        return '<User slack: %r, synapse: %r>' % (self.slack_user_id,
                                                  self.synapse_user_id)
