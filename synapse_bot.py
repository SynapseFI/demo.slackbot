import sys
import re
import traceback
from synapse_pay_rest.errors import SynapsePayError
from commands import (add_base_doc, add_node, add_physical_doc,
                      add_virtual_doc, list_nodes, list_transactions,
                      register, send, verify_node, whoami)


class SynapseBot():
    COMMANDS = {
        'add_address': add_base_doc,
        'add_node': add_node,
        'add_photo_id': add_physical_doc,
        'add_ssn': add_virtual_doc,
        'list_nodes': list_nodes,
        'list_transactions': list_transactions,
        'register': register,
        'send': send,
        'verify': verify_node,
        'whoami': whoami
    }

    def __init__(self, slack_client, bot_id):
        self.slack_client = slack_client
        self.bot_id = bot_id
        self.at_bot = '<@' + self.bot_id + '>'

    def help(self):
        """List the available bot commands."""
        return ('Available statements:\n' +
                '\n'.join([keyword for keyword in self.COMMANDS]))

    def post_to_channel(self, channel, text):
        """Post a message to the channel."""
        self.slack_client.api_call('chat.postMessage', channel=channel,
                                   text=text, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        """Monitor Slack channel for messages."""
        for output in slack_rtm_output:
            if self.is_doc_upload(output):
                self.handle_doc_upload(output)
            elif self.is_command(output):
                self.handle_command(output)

    def handle_command(self, output):
        """Check output for command keyword and call the associated function."""
        keyword, params = self.keyword_and_params_from_text(output['text'])

        if keyword == 'help':
            response = self.help()
        elif keyword in self.COMMANDS:
            response = self.execute_command(command=self.COMMANDS[keyword],
                                            user=output['user'],
                                            params=params,
                                            channel=output['channel'])
        else:
            response = 'Not sure what you mean. Try the *help* command?'
        self.post_to_channel(output['channel'], response)

    def handle_doc_upload(self, output):
        """Check comments for command keyword and add file as physical doc."""
        comment = output['file']['initial_comment']['comment']
        keyword = 'add_photo_id'  # hard-coded since there's only 1 for now
        url = output['file']['permalink']

        if keyword in comment:
            response= self.execute_command(command=self.COMMANDS[keyword],
                                           user=output['user'],
                                           params=url,
                                           channel=output['channel'])
        else:
            response = 'Not sure what you mean. Try the *add_photo_id* command?'
        self.post_to_channel(output['channel'], response)

    def execute_command(self, command, user, params, channel):
        self.acknowledge_command(channel)
        try:
            response = command(user, params)
        except SynapsePayError as e:
            response = (
                'An HTTP error occurred while trying to communicate with '
                'the Synapse API:\n{0}'.format(e.message)
            )
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            response = 'An error occurred:\n{0}'.format(sys.exc_info()[1])
        return response

    def is_command(self, output):
        """Determine whether the Slack RTM output contains a command."""
        if output and 'text' in output and self.at_bot in output['text']:
            return True

    def is_doc_upload(self, output):
        """Determine whether the Slack RTM output contains a physical doc upload.
        """
        if output and 'file' in output:
            if 'initial_comment' in output['file']:
                if self.at_bot in output['file']['initial_comment']['comment']:
                    return True

    def acknowledge_command(self, channel):
        self.post_to_channel(channel, 'Processing command...')

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
