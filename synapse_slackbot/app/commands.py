"""Commands that can be called by Synapse slackbot."""
import datetime
from synapse_pay_rest import Node, Transaction
from synapse_slackbot.config import db
from synapse_slackbot.models import User, RecurringTransaction


def whoami(slack_user_id, synapse_user, params):
    """Return info on the user."""
    return user_summary(synapse_user)


def verify_node(slack_user_id, synapse_user, params):
    """Activate a node with Synapse via microdeposits and return node info."""
    user = user_from_slack_id(slack_user_id)
    amount1 = first_word(params)
    amount2 = word_after(params, amount1)
    if not amount1 or not amount2:
        return invalid_params_warning('verify')
    node = Node.by_id(user=synapse_user, id=user.debit_node_id)
    node = node.verify_microdeposits(amount1=amount1, amount2=amount2)
    return ('*Node verified.*\n' + node_summary(node))


def list_nodes(slack_user_id, synapse_user, params):
    """Return information on the the user's Synapse nodes."""
    nodes = Node.all(user=synapse_user)
    if nodes:
        return '\n'.join([node_summary(node) for node in nodes])
    else:
        return '*No nodes found for user.*'


def balance(slack_user_id, synapse_user, params):
    """Return balance on SYNAPSE-US savings account."""
    user = user_from_slack_id(slack_user_id)
    savings_node = Node.by_id(user=synapse_user, id=user.savings_node_id)
    if savings_node:
        balance = format_currency(savings_node.balance)
        return '```savings balance: {0}```'.format(balance)
    else:
        return '*No savings node found for user.*'


def history(slack_user_id, synapse_user, params):
    """Return information on the the Synapse nodes's transactions."""
    user = user_from_slack_id(slack_user_id)
    debit_node = Node.by_id(user=synapse_user, id=user.debit_node_id)
    transactions = Transaction.all(node=debit_node)
    if transactions:
        return '\n'.join([transaction_summary(trans) for trans in transactions])
    else:
        return '*No transactions found.*'


def save(slack_user_id, synapse_user, params):
    """Create a Synapse transaction from one node to another."""
    user = user_from_slack_id(slack_user_id)
    debit_node = Node.by_id(user=synapse_user, id=user.debit_node_id)
    savings_node = Node.by_id(user=synapse_user, id=user.savings_node_id)
    amount = first_word(params)
    if not amount:
        return invalid_params_warning('send')
    if 'every' in params:
        periodicity = word_after(params, 'every')
        trans = create_recurring_transaction(amount=amount,
                                             from_id=debit_node.id,
                                             to_id=savings_node.id,
                                             periodicity=periodicity,
                                             slack_user_id=slack_user_id)
        return ('*Recurring transaction created.*\n' +
                recurring_transaction_summary(trans))
    args = {
        'amount': amount,
        'to_id': savings_node.id,
        'to_type': 'SYNAPSE-US',
        'currency': 'USD',
        'ip': '127.0.0.1'
    }
    if 'in' in params:
        args['process_in'] = word_after(params, 'in')
    transaction = Transaction.create(debit_node, **args)
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


# formatting helpers

def user_summary(synapse_user):
    """Return Markdown formatted user info."""
    return ('```'
            'Synapse user id: {0}\n'.format(synapse_user.id) +
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
           'status: {0}\n'.format(trans.recent_status['note']) +
           'from node id: {0}\n'.format(trans.node.id) +
           'to node id: {0}\n'.format(trans.to_id) +
           'created on: {0}\n'.format(timestamp_to_string(trans.created_on)) +
           'process on: {0}\n'.format(timestamp_to_string(trans.process_on)) +
           '```')


def recurring_transaction_summary(recurring):
    """Return Markdown formatted RecurringTransaction info."""
    return ('```'
            'amount: {0}\n'.format(format_currency(recurring.amount)) +
            'periodicity: every {0} days\n'.format(recurring.periodicity) +
            '```')


# general helpers

def user_from_slack_id(slack_user_id):
    return User.query.filter_by(slack_user_id=slack_user_id).first()


def invalid_params_warning(command):
    """Warning message that the format of the command is correct."""
    return ('*Please try again using the correct format:*\n'
            '> Try @synapse help')


def format_currency(amount):
    """Convert float to string currency with 2 decimal places."""
    str_format = str(amount)
    cents = str_format.split('.')[1]
    if len(cents) == 1:
        str_format += '0'
    return '{0} USD'.format(str_format)


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
