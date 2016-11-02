import sys
import re
from synapse_pay_rest.errors import SynapsePayError
from commands import (add_cip, add_physical_doc, add_virtual_doc, list_resource,
                      register, send, whoami)


class SynapseBot():
    COMMANDS = {
        'add_address': add_cip,
        'add_photo_id': add_physical_doc,
        'add_ssn': add_virtual_doc,
        'list': list_resource,
        'register': register,
        'send': send,
        'whoami': whoami
    }

    def __init__(self, slack_client, bot_id):
        self.slack_client = slack_client
        self.bot_id = bot_id
        self.at_bot = '<@' + self.bot_id + '>'

    def help(self):
        return ('Available statements:\n' +
                '\n'.join([keyword for keyword in self.COMMANDS]))

    def post_to_channel(self, channel, text):
        """Post a message to the channel."""
        self.slack_client.api_call('chat.postMessage', channel=channel,
                                   text=text, as_user=True)

    def is_command(self, output):
        if output and 'text' in output and self.at_bot in output['text']:
            return True

    def is_file_upload(self, output):
        if output and 'file' in output:
            if 'initial_comment' in output['file']:
                if self.at_bot in output['file']['initial_comment']['comment']:
                    return True

    def handle_command(self, output):
        """Parse a statement, run the matching function, post response in channel.

        Receives statements directed at the bot and determines if they
        are valid statements. If so, then acts on the statements. If not,
        returns back what it needs for clarification.
        """
        channel = output['channel']
        user = output['user']
        keyword, params = self.keyword_and_params_from_text(output['text'])

        if keyword == 'help':
            response = self.help()
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
                response = 'An error occurred:\n{0}'.format(sys.exc_info())
        else:
            response = 'Not sure what you mean. Try the *help* command?'
        self.post_to_channel(channel, response)

    def handle_file_upload(self, output):
        channel = output['channel']
        user = output['user']
        comment = output['file']['initial_comment']['comment']
        url = self.url_from_output(output)
        if 'add_photo_id' in comment:
            self.post_to_channel(channel, 'Processing command...')
            try:
                response = self.COMMANDS['add_photo_id'](user, url)
            except SynapsePayError as e:
                response = (
                    'An HTTP error occurred while trying to communicate with '
                    'the Synapse API:\n{0}'.format(e.message)
                )
            except:
                response = 'An error occurred:\n{0}'.format(sys.exc_info())
        else:
            response = 'Not sure what you mean. Try the *help* command?'
        self.post_to_channel(channel, response)

    def url_from_output(self, output):
        return output['file']['permalink']

    def parse_slack_output(self, slack_rtm_output):
        """Monitors Slack channel for messages.

        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the SynapseBot, based on its ID.
        """
        for output in slack_rtm_output:
            if self.is_file_upload(output):
                self.handle_file_upload(output)
            elif self.is_command(output):
                self.handle_command(output)

    def keyword_and_params_from_text(self, text):
        """Parse keyword and params from the text field of the Slack response.
        """
        without_bot_name = self.without_first_word(text).lower().split(' ', 1)
        keyword = without_bot_name[0]
        try:
            params = without_bot_name[1]
            params = self.purge_hyperlinks(params)
            if '|' in params:
                params = self.params_string_to_dict(params)
        except IndexError:
            params = None
        return keyword, params

    def without_first_word(self, string):
        """Return string with the first word removed."""
        return string.split(' ', 1)[1].strip()

    def params_string_to_dict(self, params):
        """Parse params in '1 a|2 b|3 c' format into {1: 'a', ...} format."""
        fields = [field.strip().split(' ', 1) for field in params.split('|')]
        return dict(fields)

    def purge_hyperlinks(self, raw):
        """Return the hyperlink-laden string with hyperlinks removed.

        TODO:
            - Probably a DRY-er way to sub with capture value in single step.
        """
        purged = raw
        email_pattern = r'<mailto:\S+\|(\S+)>'
        email = re.search(email_pattern, raw)
        if email:
            email = email.groups()[0]
            purged = re.sub(email_pattern, email, raw)
        phone_pattern = r'<tel:\S+\|(\S+)>'
        phone = re.search(phone_pattern, raw)
        if phone:
            phone = phone.groups()[0]
            purged = re.sub(phone_pattern, phone, purged)
        return purged
