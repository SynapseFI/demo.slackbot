#!/usr/bin/env python3
import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db_config import db_uri
from slackclient import SlackClient
from synapse_bot import SynapseBot

# configure Flask and postgres
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# configure slackbot
slack_client = SlackClient(os.environ.get('SLACKBOT_TOKEN'))
slackbot_id = os.environ.get('SLACKBOT_ID')
synapse_bot = SynapseBot(slack_client, slackbot_id)

# second delay between reading from firehose
READ_WEBSOCKET_DELAY = 1
if slack_client.rtm_connect():
    print('SynapseBot connected and running!')
    while True:
        stream = synapse_bot.slack_client.rtm_read()
        print(stream)
        command, channel = synapse_bot.parse_slack_output(stream)
        if command and channel:
            synapse_bot.handle_command(command, channel)
        time.sleep(READ_WEBSOCKET_DELAY)
else:
    print('Connection failed.')
