import os
import time
from config import slack_client
from bot import Bot


def start_slack_event_loop():
    """Main event loop for program."""
    bot = Bot(slack_client, os.environ['SLACKBOT_ID'])
    # second delay between reading from Slack RTM firehose
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print('Bot connected and running!')
        while True:
            stream = bot.slack_client.rtm_read()
            print(stream)
            if stream and len(stream) > 0:
                bot.parse_slack_output(stream)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed.')

# start connection to Slack streaming API
start_slack_event_loop()
