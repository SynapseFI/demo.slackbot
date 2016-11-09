"""Commands that can be called by Synapse slackbot."""
import datetime
from synapse_pay_rest import Node, Transaction
from synapse_pay_rest.models.nodes import AchUsNode, SynapseUsNode
from synapse_pay_rest import User as SynapseUser
from synapse_slackbot.config import db
from synapse_slackbot.models import User, RecurringTransaction
from synapse_slackbot.synapse_client import synapse_client


def whoami(slack_user_id, params):
    """Return info on the user."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    return user_summary(synapse_user)


def verify_node(slack_user_id, params):
    """Activate a node with Synapse via microdeposits and return node info."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    id = first_word(params)
    amount1 = word_after(params, id)
    amount2 = word_after(params, amount1)
    if not id or not amount1 or not amount2:
        return invalid_params_warning('verify')
    node = Node.by_id(user=synapse_user, id=id)
    node = node.verify_microdeposits(amount1=amount1, amount2=amount2)
    return ('*Node verified.*\n' + node_summary(node))


def list_nodes(slack_user_id, params):
    """Return information on the the user's Synapse nodes."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    nodes = Node.all(user=synapse_user)
    if nodes:
        return '\n'.join([node_summary(node) for node in nodes])
    else:
        return '*No nodes found for user.*'


def list_transactions(slack_user_id, params):
    """Return information on the the Synapse nodes's transactions."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    from_id = word_after(params, 'from')
    if not from_id:
        return invalid_params_warning('list_transactions')
    node = Node.by_id(user=synapse_user, id=from_id)
    transactions = Transaction.all(node=node)
    if transactions:
        return '\n'.join([transaction_summary(trans) for trans in transactions])
    else:
        return '*No transactions found for node.*'.format(node.id)


def send(slack_user_id, params):
    """Create a Synapse transaction from one node to another."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    amount = first_word(params)
    from_id = word_after(params, 'from')
    to_id = word_after(params, 'to')
    if not amount or not from_id or not to_id:
        return invalid_params_warning('send')
    if 'every' in params:
        periodicity = word_after(params, 'every')
        trans = create_recurring_transaction(amount=amount,
                                             from_id=from_id,
                                             to_id=to_id,
                                             periodicity=periodicity,
                                             slack_user_id=slack_user_id)
        return ('*Recurring transaction created.*\n' +
                recurring_transaction_summary(trans))
    from_node = Node.by_id(user=synapse_user, id=from_id)
    args = {
        'amount': amount,
        'to_id': to_id,
        'to_type': 'ACH-US',
        'currency': 'USD',
        'ip': '127.0.0.1'
    }
    if 'in' in params:
        args['process_in'] = word_after(params, 'in')
    transaction = Transaction.create(from_node, **args)
    return ('*Transaction created.*\n' + transaction_summary(transaction))


def create_recurring_transaction(**kwargs):
    trans = RecurringTransaction(amount=kwargs['amount'],
                                 from_node_id=kwargs['from_id'],
                                 to_node_id=kwargs['to_id'],
                                 periodicity=kwargs['periodicity'],
                                 slack_user_id=kwargs['slack_user_id'])
    db.session.add(trans)
    db.session.commit()
    return trans


# helpers

def synapse_user_from_slack_user_id(slack_user_id):
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
           'created on: {0}\n'.format(timestamp_to_string(trans.created_on)) +
           'process on: {0}\n'.format(timestamp_to_string(trans.process_on)) +
           '```')


def recurring_transaction_summary(recurring):
    """Return Markdown formatted RecurringTransaction info."""
    return ('```'
            'amount: {0}\n'.format(format_currency(recurring.amount)) +
            'from_node_id: {0}\n'.format(recurring.from_node_id) +
            'to_node_id: {0}\n'.format(recurring.to_node_id) +
            'periodicity: every {0} days\n'.format(recurring.periodicity) +
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
