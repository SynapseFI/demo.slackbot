import sys
import traceback
from synapse_pay_rest import User as SynapseUser
from synapse_pay_rest.errors import SynapsePayError
from models import User
from config import synapse_client
from commands import balance, cancel, history, list_nodes, save, verify_node,\
                      whoami


class Bot():
    """Provides a limited Slack interface for the Synapse API."""

    COMMANDS = {
        'whoami': {
            'function_name': whoami,
            'example': '@synapse whoami',
            'description': 'Return basic information about the user:'
        },
        'balance': {
            'function_name': balance,
            'example': '@synapse balance',
            'description': 'List savings balance:'
        },
        'save': {
            'function_name': save,
            'example': ('@synapse save `[amount]` (in `[number]` '
                        'days) / (every `[number]` days)'),
            'description': 'Schedule a one-time or recurring savings transfer:'
        },
        'cancel': {
            'function_name': cancel,
            'example': ('@synapse cancel `[transaction_id]`'),
            'description': ('Cancel a transaction that has not yet settled:')
        },
        'history': {
            'function_name': history,
            'example': '@synapse history',
            'description': 'List most recent transaction history:'
        },
        'nodes': {
            'function_name': list_nodes,
            'example': '@synapse nodes',
            'description': 'List the bank accounts associated with the user:'
        },
        'verify': {
            'function_name': verify_node,
            'example': ('@synapse verify `[microdeposit amount 1]` '
                        '`[microdeposit amount 2]`'),
            'description': 'Activate a node by verifying micro-deposit amounts:'
        }
    }

    def __init__(self, slack_client, bot_id):
        self.slack_client = slack_client
        self.bot_id = bot_id
        self.at_bot = '<@' + self.bot_id + '>'

    def help(self):
        """List the available bot commands with descriptions and examples."""
        help_strings = [
            '*{0}*\n'.format(self.COMMANDS[keyword]['description']) +
            '>{0}'.format(self.COMMANDS[keyword]['example'])
            for keyword in self.COMMANDS
        ]
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
            if output and 'text' in output and self.at_bot in output['text']:
                self.handle_command(output)

    def handle_command(self, output):
        """Check message for command keyword and call associated function."""
        keyword, params = self.keyword_and_params_from_text(output['text'])

        if keyword == 'help':
            response = self.help()
        elif keyword in self.COMMANDS:
            response = self.execute_command(
                command=self.COMMANDS[keyword]['function_name'],
                slack_id=output['user'],
                params=params,
                channel=output['channel']
            )
        else:
            response = ('*Not sure what you mean. Try this:*\n>@synapse help')
        self.post_to_channel(output['channel'], response)

    def execute_command(self, command, slack_id, params, channel):
        """Attempt to run the command with the parameters provided."""
        self.acknowledge_command(channel)
        synapse_user = self.synapse_user_from_slack_user_id(slack_id)
        self.post_to_channel(channel, 'synapse_user: {0}'.format(synapse_user))
        response = self.registration_prompt(slack_id)

        if synapse_user:
            try:
                response = command(slack_id, synapse_user, params)
            except SynapsePayError as e:
                response = (
                    'An HTTP error occurred while trying to communicate with '
                    'the Synapse API:\n{0}'.format(e.message)
                )
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                response = 'An error occurred:\n{0}: {1}'.format(
                    sys.exc_info()[0],sys.exc_info()[1]
                )
        self.post_to_channel(channel, 'response: {0}'.format(response))
        return response

    def acknowledge_command(self, channel):
        """Post a message to channel acknowledging receipt of command."""
        self.post_to_channel(channel, 'Processing command...')

    def verify_registration(self, synapse_id):
        synapse_user = self.synapse_user_from_slack_user_id(self.slack_user_id)
        if not synapse_user:
            return False
        return synapse_user

    def synapse_user_from_slack_user_id(self, slack_user_id):
        """Find the Slack user's Synapse ID and get the Synapse user."""
        user = User.query.filter_by(slack_user_id=slack_user_id).first()
        if user is None:
            return None
        return SynapseUser.by_id(client=synapse_client, id=user.synapse_user_id)

    def registration_prompt(self, slack_id):
        """Warning message that the user needs to register first."""
        return ('*Please register first!*\n'
                '> http://104.236.189.18/register/{0}'.format(slack_id))

    # helpers

    def keyword_and_params_from_text(self, text):
        """Parse keyword and params from the Slack message."""
        try:
            bot_name_stripped = self.without_first_word(text).lower().split(' ',
                                                                            1)
        except:
            return None, None
        keyword = bot_name_stripped[0]
        try:
            params = bot_name_stripped[1]
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
