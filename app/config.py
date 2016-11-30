"""General settings and database initialization."""
import os
from flask import Flask
from slackclient import SlackClient
from synapse_pay_rest import Client
from db import connect_db

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
FINGERPRINT = os.environ['FINGERPRINT']
SLACKBOT_TOKEN = os.environ['SLACKBOT_TOKEN']

app = Flask(__name__)
# app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = connect_db(app=app,
                username='stevula',
                password='default',
                host='159.203.245.190',
                port=5432,
                database='slackbot')

slack_client = SlackClient(SLACKBOT_TOKEN)

synapse_client = Client(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    fingerprint=FINGERPRINT,
    ip_address='127.0.0.1',
    logging=True,
    development_mode=True
)
