import os
from flask import Flask
from slackclient import SlackClient
from .db import initialize_db

# Flask config
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB config
db = initialize_db(app=app,
                   username='stevula',
                   password='default',
                   host='localhost',
                   port=5432,
                   database='slackbot')

slack_client = SlackClient(os.environ.get('SLACKBOT_TOKEN'))
