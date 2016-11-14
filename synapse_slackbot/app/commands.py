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
    user = User.from_slack_id(slack_user_id)
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
    user = User.from_slack_id(slack_user_id)
    savings_node = Node.by_id(user=synapse_user, id=user.savings_node_id)
    if savings_node:
        balance = format_currency(savings_node.balance)
        return '```Savings: {0}```'.format(balance)
    else:
        return '*No savings node found for user.*'


def history(slack_user_id, synapse_user, params):
    """Return information on the the Synapse nodes's transactions."""
    user = User.from_slack_id(slack_user_id)
    debit_node = Node.by_id(user=synapse_user, id=user.debit_node_id)
    transactions = Transaction.all(node=debit_node)
    if transactions:
        return '\n'.join([transaction_summary(trans) for trans in transactions])
    else:
        return '*No transactions found.*'


def save(slack_user_id, synapse_user, params):
    """Create a Synapse transaction from one node to another."""
    user = User.from_slack_id(slack_user_id)
    debit_node = Node.by_id(user=synapse_user, id=user.debit_node_id)
    savings_node = Node.by_id(user=synapse_user, id=user.savings_node_id)
    amount = first_word(params)
    if not amount:
        # invalid params
        return invalid_params_warning('send')

    if 'every' in params:
        # recurring transaction
        periodicity = word_after(params, 'every')
        return create_recurring_transaction(amount=amount,
                                            from_id=debit_node.id,
                                            to_id=savings_node.id,
                                            periodicity=periodicity,
                                            slack_user_id=slack_user_id)

    process_in = None
    if 'in' in params:
        # scheduled transaction
        process_in = word_after(params, 'in')

    return create_transaction(amount=amount,
                              debit_node=debit_node,
                              savings_node_id=savings_node.id,
                              process_in=process_in)


def create_transaction(**kwargs):
    """Create a standard Synapse transaction (default or scheduled)."""
    args = {
        'amount': kwargs['amount'],
        'to_id': kwargs['savings_node_id'],
        'to_type': 'SYNAPSE-US',
        'currency': 'USD',
        'ip': '127.0.0.1'
    }
    if kwargs.get('process_in'):
        args['process_in'] = kwargs['process_in']
    transaction = Transaction.create(kwargs['debit_node'], **args)
    return ('*Transaction created.*\n' + transaction_summary(transaction))


def create_recurring_transaction(**kwargs):
    """Create a RecurringTransaction."""
    trans = RecurringTransaction(amount=kwargs['amount'],
                                 from_node_id=kwargs['from_id'],
                                 to_node_id=kwargs['to_id'],
                                 periodicity=kwargs['periodicity'],
                                 slack_user_id=kwargs['slack_user_id'])
    db.session.add(trans)
    db.session.commit()
    return ('*Recurring transaction created.*\n' +
            recurring_transaction_summary(trans))


# formatting helpers

def user_summary(synapse_user):
    """Return Markdown formatted user info."""
    return ('```'
            'Synapse user id: {0}\n'.format(synapse_user.id) +
            'Name: {0}\n'.format(synapse_user.legal_names[0]) +
            'Permissions: {0}\n'.format(synapse_user.permission) +
            '```')


def node_summary(node):
    """Return Markdown formatted node info."""
    return ('```'
            'Node id: {0}\n'.format(node.id) +
            'Nickname: {0}\n'.format(node.nickname) +
            'Type: {0}\n'.format(node.account_class) +
            'Permissions: {0}\n'.format(node.permission) +
            '```')


def transaction_summary(trans):
    """Return Markdown formatted transaction info."""
    return('```'
           'Trans id: {0}\n'.format(trans.id) +
           'Amount: {0}\n'.format(format_currency(trans.amount)) +
           'Status: {0}\n'.format(trans.recent_status['note']) +
           'From node id: {0}\n'.format(trans.node.id) +
           'To node id: {0}\n'.format(trans.to_id) +
           'Created on: {0}\n'.format(timestamp_to_string(trans.created_on)) +
           'Process on: {0}\n'.format(timestamp_to_string(trans.process_on)) +
           '```')


def recurring_transaction_summary(recurring):
    """Return Markdown formatted RecurringTransaction info."""
    return ('```'
            'Amount: {0}\n'.format(format_currency(recurring.amount)) +
            'Periodicity: every {0} days\n'.format(recurring.periodicity) +
            '```')


# general helpers

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
