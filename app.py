#!/usr/bin/env python3
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db_config import db_uri
from bot import slack_client, parse_slack_output, handle_command

# configure Flask and postgres
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# second delay between reading from firehose
while True:
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print('StarterBot connected and running!')
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')
