import sys
from synapse_pay_rest.errors import SynapsePayError
from commands import i_am, list_resource, send, who_am_i


class SynapseBot():
    COMMANDS = {
        'list': list_resource,
        'iam': i_am,
        'send': send,
        'whoami': who_am_i
    }

    def __init__(self, slack_client, bot_id):
        self.slack_client = slack_client
        self.bot_id = bot_id

    def at_bot(self):
        return '<@' + self.bot_id + '>'

    def handle_command(self, command, channel):
        """Parses a command, runs the matching function, posts response in channel.

        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
        """
        response = 'Not sure what you mean. Try the *help* command?'
        keyword = command.lower().split(' ', 1)[0]
        if keyword == 'help':
            response = (
                'Available commands:\n' +
                '\n'.join([command for command in self.COMMANDS])
            )
        elif keyword in self.COMMANDS:
            try:
                response = self.COMMANDS[keyword](command)
            except SynapsePayError as e:
                response = (
                    'An HTTP error occurred while trying to communicate with '
                    'the Synapse API:\n{0}'.format(e.message)
                )
            except:
                response = (
                    'An error occurred:\n{0}'.format(sys.exc_info()[0])
                )

        self.slack_client.api_call("chat.postMessage", channel=channel,
                                   text=response, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        """Monitors Slack channel for messages.

        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the SynapseBot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self.at_bot() in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(self.at_bot())[1].strip().lower(), \
                           output['channel']
        return None, None
