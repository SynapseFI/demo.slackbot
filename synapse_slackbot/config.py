"""General settings and database initialization."""
import os
from flask import Flask
from slackclient import SlackClient
from .db import connect_db

# Flask config
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB config
db = connect_db(app=app,
                username='stevula',
                password='default',
                host='localhost',
                port=5432,
                database='slackbot')

# SlackClient config
slack_client = SlackClient(os.environ.get('SLACKBOT_TOKEN'))
