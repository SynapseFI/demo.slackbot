"""Commands that can be called by Synapse slackbot."""
import datetime
import os
from synapse_pay_rest import Client, Node, Transaction
from synapse_pay_rest import User as SynapseUser
from db_config import db
from models import User


synapse_client = Client(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    fingerprint=os.environ['FINGERPRINT'],
    ip_address='127.0.0.1',
    logging=True,
    development_mode=True
)


def register(slack_user_id, command):
    """Create a new user with Synapse.

    TODO:
        - better way to parse names > 2 words length
        - split these out into separate commands?
    """
    first_name = word_after(command, 'name')
    last_name = word_after(command, first_name)
    name = first_name + ' ' + last_name
    mailto = word_after(command, 'email')
    tel = word_after(command, 'phone')
    email = parse_mailto_or_tel(mailto)
    phone = parse_mailto_or_tel(tel)
    options = {
        'note': 'created by Synapse Slackbot',
        'supp_id': '',
        'is_business': False,
        'cip_tag': 1
    }
    synapse_user = SynapseUser.create(client=synapse_client, email=email,
                                      phone_number=phone, legal_name=name,
                                      **options)
    user = User(slack_user_id, synapse_user.id)
    db.session.add(user)
    db.session.commit()
    return 'User created - {0} (user_id: {1})'.format(synapse_user.legal_names[0],
                                                      synapse_user.id)


def add_cip(slack_user_id, command):
    """Add Synapse CIP base document to user."""
    pass


def who_am_i(slack_user_id, command):
    """Return info on the user."""
    user = User.query.filter(User.slack_user_id==slack_user_id).all()[-1]
    synapse_user = SynapseUser.by_id(client=synapse_client, id=user.synapse_user_id)
    return 'You are {0} (user_id: {1})'.format(synapse_user.legal_names[0], synapse_user.id)


def list_resource(slack_user_id, command):
    """List the specified resource (node/transaction)."""
    resource = word_after(command, 'list')
    if resource == 'nodes':
        return list_nodes()
    elif resource == 'transactions':
        from_id = word_after(command, 'from')
        return list_transactions(from_id)


def list_nodes():
    """Return the user's Synapse nodes."""
    nodes = Node.all(user=user)
    formatted = ['{0} - {1} (node_id: {2})'.format(node.type,
                                                   node.nickname,
                                                   node.id)
                 for node in nodes]
    return '\n'.join(formatted)


def list_transactions(from_id):
    """Return the user's Synapse transactions."""
    node = Node.by_id(user=user, id=from_id)
    transactions = Transaction.all(node=node)
    formatted = ["You sent {0} on {1} to {2}'s {3} node "
                 "(trans_id: {4}).".format(
                        format_currency(trans.amount),
                        timestamp_to_string(trans.process_on),
                        trans.to_info['user']['legal_names'][0],
                        trans.to_info['type'],
                        trans.id
                    )
                 for trans in transactions]
    return '\n'.join(formatted)


def send(slack_user_id, command):
    """Create a Synapse transaction."""
    from_node_id = word_after(command, 'from')
    from_node = Node.by_id(user=user, id=from_node_id)
    args = {
        'amount': word_after(command, 'send'),
        'to_id': word_after(command, 'to'),
        'to_type': 'SYNAPSE-US',
        'currency': 'USD',
        'ip': '127.0.0.1'
    }
    if 'on' in command:
        args['process_in'] = word_after(command, 'in')
    try:
        transaction = Transaction.create(from_node, **args)
    except Exception as e:
        print(e.__dict__)
    return (
        "Created ${0} transaction from {1}'s {2} node to {3}'s {4} node.\n"
        "Scheduled for {5}.\nCurrent status: {6}.".format(
            format_currency(transaction.amount),
            transaction.from_info['user']['legal_names'][0],
            transaction.from_info['type'],
            transaction.to_info['user']['legal_names'][0],
            transaction.to_info['type'],
            timestamp_to_string(transaction.process_on),
            transaction.recent_status['note']
        )
    )


# helpers
def synapse_id_from_slack_id(slack_id):
    """Look up user's synapse_user_id in database."""


def format_currency(amount):
    """Convert float to string currency with 2 decimal places."""
    str_format = str(amount)
    cents = str_format.split('.')[1]
    if len(cents) == 1:
        str_format += '0'
    return str_format


def word_after(sentence, word):
    """Return the word following the given word in the sentence string."""
    words = sentence.split()
    index = words.index(word) + 1
    return words[index]


def timestamp_to_string(timestamp):
    """Convert a 13-digit UNIX timestamp to a formatted datetime string."""
    without_ms = int(str(timestamp)[:-3])
    timestamp = datetime.datetime.fromtimestamp(without_ms)
    return timestamp.strftime('%Y-%m-%d')


def parse_mailto_or_tel(mailto_string):
    return mailto_string.split('|')[1][:-1]
