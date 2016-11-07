import datetime
from synapse_pay_rest import User as SynapseUser
from .models import User
from .commands_directory import COMMANDS


# helpers
def synapse_user_from_slack_user_id(synapse_client, slack_user_id):
    """Find the Slack user's Synapse id and get the Synapse user."""
    user = User.query.filter_by(slack_user_id=slack_user_id).first()
    if user is None:
        return None
    return SynapseUser.by_id(client=synapse_client, id=user.synapse_user_id)


def format_currency(amount):
    """Convert float to string currency with 2 decimal places."""
    str_format = str(amount)
    cents = str_format.split('.')[1]
    if len(cents) == 1:
        str_format += '0'
    return str_format


def first_word(sentence):
    """Return first word of a string."""
    try:
        return sentence.split(' ', 1)[0]
    except:
        return None


def word_after(sentence, word):
    """Return the word following the given word in the sentence string."""
    try:
        words = sentence.split()
        index = words.index(word) + 1
        return words[index]
    except:
        return None


def timestamp_to_string(timestamp):
    """Convert a 13-digit UNIX timestamp to a formatted datetime string."""
    without_ms = int(str(timestamp)[:-3])
    timestamp = datetime.datetime.fromtimestamp(without_ms)
    return timestamp.strftime('%Y-%m-%d')


def string_date_to_ints(bday):
    """Split mm/dd/yy(yy) into separate m, d, and y fields."""
    try:
        month, day, year = [int(num) for num in bday.split('/')]
        return month, day, year
    except:
        return None, None, None


def user_summary(synapse_user):
    """Return Markdown formatted user info."""
    return ('```'
            'user id: {0}\n'.format(synapse_user.id) +
            'name: {0}\n'.format(synapse_user.legal_names[0]) +
            'permissions: {0}\n'.format(synapse_user.permission) +
            '```')


def node_summary(node):
    """Return Markdown formatted node info."""
    return ('```'
            'node id: {0}\n'.format(node.id) +
            'nickname: {0}\n'.format(node.nickname) +
            'type: {0}\n'.format(node.account_class) +
            'permissions: {0}\n'.format(node.permission) +
            '```')


def transaction_summary(trans):
    """Return Markdown formatted transaction info."""
    return('```'
           'trans id: {0}\n'.format(trans.id) +
           'amount: {0}\n'.format(format_currency(trans.amount)) +
           'from node id: {0}\n'.format(trans.node.id) +
           'to node id: {0}\n'.format(trans.to_id) +
           'recipient name: {0}\n'.format(trans.to_info['user']['legal_names'][0]) +
           'status: {0}\n'.format(trans.recent_status['note']) +
           'created_on: {0}\n'.format(timestamp_to_string(trans.created_on)) +
           'process on: {0}\n'.format(timestamp_to_string(trans.process_on)) +
           '```')


def registration_warning():
    """Warning message that the user needs to register first."""
    return ('*You need to register first!*\n'
            '>' + COMMANDS['register']['example'])


def base_doc_warning():
    return ('*You need to provide your address first!*\n'
            '>' + COMMANDS['add_address']['example'])


def invalid_params_warning(command):
    """Warning message that the format of the command is correct."""
    return ('*Please try again using the correct format:*\n'
            '>' + COMMANDS[command]['example'])
