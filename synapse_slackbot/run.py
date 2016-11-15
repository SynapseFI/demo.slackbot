#!/usr/bin/env python3
"""Main Slackbot event loop and routes."""
import time
import os
import _thread
from flask import jsonify, render_template, request
from .config import app, slack_client
from .app.synapse_bot import SynapseBot
from .models import User

synapse_bot = SynapseBot(slack_client, os.environ.get('SLACKBOT_ID'))


@app.route('/register/<slack_id>', methods=['GET', 'POST'])
def register(slack_id):
    """Route for handling user registration form."""
    if request.method == 'GET':
        return render_template('register.html', slack_id=slack_id)
    elif request.method == 'POST':
        if User.from_slack_id(slack_id):
            response = jsonify({
                'message': 'You are already registered with this Slack ID.'
            })
            response.status_code = 409
            return response
        try:
            User.from_request(slack_id, request)
            response = jsonify({'message': 'You are now registered.'})
            response.status_code = 200
        except Exception as e:
            response = jsonify({'message': 'Sorry, server error.'})
            response.status_code = 500
        return response


def start_bot_event_loop():
    """Main event loop for program."""
    # second delay between reading from Slack RTM firehose
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print('SynapseBot connected and running!')
        while True:
            stream = synapse_bot.slack_client.rtm_read()
            print(stream)
            if stream and len(stream) > 0:
                synapse_bot.parse_slack_output(stream)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed.')

_thread.start_new_thread(start_bot_event_loop, ())
app.run()
