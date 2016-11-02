#!/usr/bin/env python3
import os
import time
from slackclient import SlackClient
from synapse_bot import SynapseBot

# configure slackbot
slack_client = SlackClient(os.environ.get('SLACKBOT_TOKEN'))
slackbot_id = os.environ.get('SLACKBOT_ID')
synapse_bot = SynapseBot(slack_client, slackbot_id)

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
