#!/usr/bin/env python3
import time
import os
from .config import slack_client
from .app.synapse_bot import SynapseBot

synapse_bot = SynapseBot(slack_client, os.environ.get('SLACKBOT_ID'))

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
