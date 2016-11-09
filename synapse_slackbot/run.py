#!/usr/bin/env python3
"""Start event loop."""
import time
import os
import _thread
from flask import render_template
from .config import app
from .config import slack_client
from .app.synapse_bot import SynapseBot

synapse_bot = SynapseBot(slack_client, os.environ.get('SLACKBOT_ID'))


@app.route('/register/<slack_id>', methods=['GET', 'POST'])
def register(slack_id):
    return render_template('register.html')


def startEventLoop():
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

if __name__ == '__main__':
    app.run()
    _thread.start_new_thread(startEventLoop, ())
