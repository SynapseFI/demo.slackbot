"""General settings and database initialization."""
import os
from flask import Flask
from slackclient import SlackClient
from synapse_pay_rest import Client
from db import connect_db

app = Flask(__name__)
# app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = connect_db(app=app,
                username='stevula',
                password='default',
                host='localhost',
                port=5432,
                database='slackbot')

slack_client = SlackClient(os.environ.get('SLACKBOT_TOKEN'))

synapse_client = Client(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    fingerprint=os.environ['FINGERPRINT'],
    ip_address='127.0.0.1',
    logging=True,
    development_mode=True
)
