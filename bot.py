import os
import sys
from slackclient import SlackClient
from synapse_pay_rest.errors import SynapsePayError
from commands import list_resource, send, who_am_i

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACKBOT_TOKEN'))

# bot constants
BOT_ID = os.environ.get('SLACKBOT_ID')
AT_BOT = '<@' + BOT_ID + '>'
COMMANDS = {
    'list': list_resource,
    'send': send,
    'whoami': who_am_i
}


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = 'Not sure what you mean. Try the *help* command?'
    keyword = command.split(' ', 1)[0]
    if keyword == 'help':
        response = (
            'Available commands:\n' +
            '\n'.join([command for command in COMMANDS])
        )
    elif keyword in COMMANDS:
        try:
            response = COMMANDS[keyword](command)
        except SynapsePayError as e:
            response = (
                'An HTTP error occurred while trying to communicate with '
                'the Synapse API:\n{0}'.format(e.message)
            )
        except:
            response = (
                'An error occurred:\n{0}'.format(sys.exc_info()[0])
            )

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None
