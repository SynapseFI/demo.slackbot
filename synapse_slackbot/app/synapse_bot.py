import sys
import re
import traceback
from synapse_pay_rest.errors import SynapsePayError
from .commands_directory import COMMANDS


class SynapseBot():
    """Provides a limited Slack interface for the Synapse API."""

    def __init__(self, slack_client, bot_id):
        self.slack_client = slack_client
        self.bot_id = bot_id
        self.at_bot = '<@' + self.bot_id + '>'

    def help(self):
        """List the available bot commands with descriptions and examples."""
        help_strings = ['*{0}*\n'.format(COMMANDS[keyword]['description']) +
                        '>{0}'.format(COMMANDS[keyword]['example'])
                        for keyword in COMMANDS]
        return '\n\n'.join(help_strings)

    def post_to_channel(self, channel, text):
        """Post a message to the channel as bot.

        TODO:
            - Auto-delete this message when returning command response.
        """
        self.slack_client.api_call('chat.postMessage', channel=channel,
                                   text=text, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        """Monitor Slack messages for @synapse mentions and react if found."""
        for output in slack_rtm_output:
            if self.is_doc_upload(output):
                self.handle_doc_upload(output)
            elif self.is_command(output):
                self.handle_command(output)

    def handle_command(self, output):
        """Check message for command keyword and call associated function."""
        keyword, params = self.keyword_and_params_from_text(output['text'])

        if keyword == 'help':
            response = self.help()
        elif keyword in COMMANDS:
            command = COMMANDS[keyword]['function_name']
            response = self.execute_command(command=command,
                                            user=output['user'],
                                            params=params,
                                            channel=output['channel'])
        else:
            response = ('*Not sure what you mean. Try this:*\n>@synapse help')
        self.post_to_channel(output['channel'], response)

    def handle_doc_upload(self, output):
        """Check file upload for command keyword and call associated function.
        """
        comment = output['file']['initial_comment']['comment']
        keyword = 'add_photo_id'  # hard-coded since there's only 1 for now
        url = output['file']['permalink']

        if keyword in comment:
            command = COMMANDS[keyword]['function_name']
            response = self.execute_command(command=command,
                                            user=output['user'],
                                            params=url,
                                            channel=output['channel'])
        else:
            response = ('*Not sure what you mean. Try this:*\n>@synapse help')
        self.post_to_channel(output['channel'], response)

    def execute_command(self, command, user, params, channel):
        """Attempt to run the command with the parameters provided."""
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
            response = 'An error occurred:\n{0}: {1}'.format(sys.exc_info()[0],
                                                             sys.exc_info()[1])
        return response

    def is_command(self, output):
        """Determine whether Slack output contains a message with a command."""
        if output and 'text' in output and self.at_bot in output['text']:
            return True

    def is_doc_upload(self, output):
        """Determine whether Slack output contains an upload with a command."""
        if output and 'file' in output:
            if 'initial_comment' in output['file']:
                if self.at_bot in output['file']['initial_comment']['comment']:
                    return True

    def acknowledge_command(self, channel):
        """Post a message to channel acknowledging receipt of command."""
        self.post_to_channel(channel, 'Processing command...')

    def keyword_and_params_from_text(self, text):
        """Parse keyword and params from the Slack message."""
        try:
            without_bot_name = self.without_first_word(text).lower().split(' ', 1)
        except:
            return None, None
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
        try:
            return string.split(' ', 1)[1].strip()
        except:
            return None

    def params_string_to_dict(self, params):
        """Parse params in '1 a|2 b|3 c' format into {1: 'a', ...} format."""
        fields = [field.strip().split(' ', 1) for field in params.split('|')]
        for field in fields:
            if len(field) is not 2:
                fields.remove(field)
        return dict(fields)

    def purge_hyperlinks(self, raw):
        """Return the hyperlink-laden string with hyperlinks removed.

        TODO:
            - DRY-er way to sub with capture value in single step.
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
