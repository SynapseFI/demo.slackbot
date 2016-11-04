"""SQLAlchemy models."""
from config import db


class User(db.Model):
    """Store slack user id and synapse user id.

    Todo:
        - Index slack_user_id
    """
    slack_user_id = db.Column(db.String(15), primary_key=True)
    synapse_user_id = db.Column(db.String(30), unique=True)

    def __init__(self, slack_user_id, synapse_user_id):
        self.slack_user_id = slack_user_id
        self.synapse_user_id = synapse_user_id

    def __repr__(self):
        return '<User slack: %r, synapse: %r>' % (self.slack_user_id,
                                                  self.synapse_user_id)
