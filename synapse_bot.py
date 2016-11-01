import sys
import re
from synapse_pay_rest.errors import SynapsePayError
from commands import add_cip, list_resource, register, send, who_am_i


class SynapseBot():
    COMMANDS = {
        'cip': add_cip,
        'list': list_resource,
        'register': register,
        'send': send,
        'whoami': who_am_i
    }

    def __init__(self, slack_client, bot_id):
        self.slack_client = slack_client
        self.bot_id = bot_id

    def at_bot(self):
        """The format of the bot id that matches the Slack API return value."""
        return '<@' + self.bot_id + '>'

    def post_to_channel(self, channel, text):
        """Post a message to the channel."""
        self.slack_client.api_call('chat.postMessage', channel=channel,
                                   text=text, as_user=True)

    def handle_statement(self, channel, user, keyword, params):
        """Parse a statement, run the matching function, post response in channel.

        Receives statements directed at the bot and determines if they
        are valid statements. If so, then acts on the statements. If not,
        returns back what it needs for clarification.
        """
        if keyword == 'help':
            response = (
                'Available statements:\n' +
                '\n'.join([keyword for keyword in self.COMMANDS])
            )
        elif keyword in self.COMMANDS:
            self.post_to_channel(channel, 'Processing command...')
            try:
                action = self.COMMANDS[keyword]
                response = action(user, params)
            except SynapsePayError as e:
                response = (
                    'An HTTP error occurred while trying to communicate with '
                    'the Synapse API:\n{0}'.format(e.message)
                )
            except:
                response = 'An error occurred:\n{0}'.format(sys.exc_info()[0])
        else:
            response = 'Not sure what you mean. Try the *help* command?'
        self.post_to_channel(channel, response)

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
                    keyword, params = self.keyword_and_params_from_text(output['text'])
                    return (output['channel'], output['user'], keyword, params)
        return None, None, None, None

    def keyword_and_params_from_text(self, text):
        """Parse keyword and params from the text field of the Slack response.
        """
        without_bot_name = self.without_first_word(text).lower().split(' ', 1)
        keyword = without_bot_name[0]
        try:
            params = without_bot_name[1]
            params = self.purge_hyperlinks(params)
            params = self.params_string_to_dict(params)
        except IndexError:
            params = None
        return keyword, params

    def without_first_word(self, string):
        """Return string with the first word removed."""
        return string.split(' ', 1)[1].strip()

    def params_string_to_dict(self, params):
        """Parse params in '1 a|2 b|3 c' format into {1: 'a', ...} format."""
        fields = params.split('|')
        field_values = {}
        for field in fields:
            field = field.strip()
            field_name, value = field.split(' ', 1)
            field_name = field_name.strip()
            value = value.strip()
            field_values[field_name] = value
        return field_values

    def purge_hyperlinks(self, hyperlinked):
        """Return the hyperlink-laden string with hyperlinks removed."""
        email_pattern = r'<mailto:\S+\|(\S+)>'
        email = re.search(email_pattern, hyperlinked).groups()[0]
        purged = re.sub(email_pattern, email, hyperlinked)
        phone_pattern = r'<tel:\S+\|(\S+)>'
        phone = re.search(phone_pattern, hyperlinked).groups()[0]
        purged = re.sub(phone_pattern, phone, purged)
        return purged
