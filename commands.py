"""Commands that can be called by Synapse slackbot."""
import datetime
import os
from synapse_pay_rest import Client, Node, Transaction
from synapse_pay_rest.models.nodes import AchUsNode
from synapse_pay_rest import User as SynapseUser
from config import db
from models import User

# temporary
server_ip = '127.0.0.1'

# initialize synapse client
synapse_client = Client(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    fingerprint=os.environ['FINGERPRINT'],
    ip_address=server_ip,
    logging=True,
    development_mode=True
)


def register(slack_user_id, params):
    """Create a new user with Synapse and return user info.

    TODO:
        - accept these as separate msgs instead of | delimited
    """
    for required in ['email', 'phone', 'name']:
        if not params or required not in params:
            return invalid_params_warning('register')

    # these 'options' actually required until pending API update or lib change
    options = {
        'note': 'created by Synapse Slackbot',
        'supp_id': slack_user_id,
        'is_business': False,
        'cip_tag': 1
    }
    synapse_user = SynapseUser.create(client=synapse_client,
                                      email=params['email'],
                                      phone_number=params['phone'],
                                      legal_name=params['name'].title(),
                                      **options)
    user = User(slack_user_id, synapse_user.id)
    db.session.add(user)
    db.session.commit()
    return user_summary(synapse_user)


def whoami(slack_user_id, params):
    """Return info on the user.

    TODO:
        - should not choke if the user isn't registered yet
    """
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    return user_summary(synapse_user)


def add_base_doc(slack_user_id, params):
    """Add Synapse CIP base document to user and return user info."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    for required in ['street', 'city', 'state', 'zip', 'dob']:
        if not params or required not in params:
            return invalid_params_warning('add_address')
    day, month, year = string_date_to_ints(params['dob'])
    for required in [day, month, year]:
        if not required:
            return invalid_params_warning('add_address')
    name = synapse_user.legal_names[0]
    doc = synapse_user.add_base_document(
        ip=server_ip,
        name=name.title(),
        alias=name.title(),
        birth_day=day,
        birth_month=month,
        birth_year=year,
        email=synapse_user.logins[0]['email'],
        phone_number=synapse_user.phone_numbers[0],
        entity_type='NOT_KNOWN',
        entity_scope='Not Known',
        address_street=params['street'].title(),
        address_city=params['city'].title(),
        address_subdivision=params['state'].upper(),
        address_postal_code=params['zip'],
        address_country_code='US'
    )
    synapse_user = doc.user
    return ('*Base document added.*\n' + user_summary(synapse_user))


def add_physical_doc(slack_user_id, params):
    """Upload a physical doc for user's CIP."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    base_doc = synapse_user.base_documents[-1]
    physical_doc = base_doc.add_physical_document(type='GOVT_ID', url=params)
    synapse_user = physical_doc.base_document.user
    return ('*GOVT_ID added.*\n' + user_summary(synapse_user))


def add_virtual_doc(slack_user_id, params):
    """Add a virtual doc for user's CIP and return user info."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    if not params:
        return invalid_params_warning('add_ssn')
    if not synapse_user.base_documents:
        return base_doc_warning()
    base_doc = synapse_user.base_documents[-1]
    virtual_doc = base_doc.add_virtual_document(type='SSN', value=params)
    synapse_user = virtual_doc.base_document.user
    return ('*SSN added.*\n' + user_summary(synapse_user))


def add_node(slack_user_id, params):
    """Add a node to the user in Synapse and return node info."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    if not synapse_user:
        return registration_warning()
    for required in ['nickname', 'account', 'routing', 'type']:
        if not params or required not in params:
            return invalid_params_warning('add_node')
    node = AchUsNode.create(synapse_user,
                            nickname=params['nickname'].title(),
                            account_number=params['account'],
                            routing_number=params['routing'],
                            account_type='PERSONAL',
                            account_class=params['type'].upper())
    return ('*Node added.*\n' + node_summary(node))


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
    from_node = Node.by_id(user=synapse_user, id=from_id)
    args = {
        'amount': amount,
        'to_id': to_id,
        'to_type': 'ACH-US',
        'currency': 'USD',
        'ip': server_ip
    }
    if 'on' in params:
        args['process_in'] = word_after(params, 'in')
    transaction = Transaction.create(from_node, **args)
    return ('*Transaction created.*\n' + transaction_summary(transaction))


COMMANDS = {
    'add_address': {
        'function_name': add_base_doc,
        'example': ('@synapse add_address street `[street address]` | '
                    'city `[city]` | state `[state abbreviation]` | zip '
                    '`[zip]` | dob `[mm/dd/yyyy]`'),
        'description': "Provide the user's address:"
    },
    'add_node': {
        'function_name': add_node,
        'example': ('@synapse add_node nickname `[nickname]` | account '
                    '`[account number]` | routing `[routing number]` | '
                    'type `[CHECKING / SAVINGS]`'),
        'description': 'Associate a bank account with the user:'
    },
    'add_photo_id': {
        'function_name': add_physical_doc,
        'example': '@synapse add_photo_id',
        'description': ("Provide the user's photo ID by uploading a file "
                        'with this comment')
    },
    'add_ssn': {
        'function_name': add_virtual_doc,
        'example': '@synapse add_ssn `[last four digits of ssn]`',
        'description': "Provide the user's SSN:"
    },
    'list_nodes': {
        'function_name': list_nodes,
        'example': '@synapse list_nodes',
        'description': 'List the bank accounts associated with the user:'
    },
    'list_transactions': {
        'function_name': list_transactions,
        'example': '@synapse list_transactions from `[id of sending node]`',
        'description': 'List the transactions sent from a specific node:'
    },
    'register': {
        'function_name': register,
        'example': ('@synapse register name `[first last]` | email '
                    '`[email address]` | phone `[phone number]`'),
        'description': 'Register a user with Synapse:'
    },
    'send': {
        'function_name': send,
        'example': ('@synapse send `[amount]` from `[id of sending node]` '
                    'to `[id of receiving node]` *[optional]* in '
                    '`[number]` days'),
        'description': ('Create a transaction to move funds from one node '
                        'to another:')
    },
    'verify': {
        'function_name': verify_node,
        'example': ('@synapse verify `[node id]` `[microdeposit amount '
                    '1]` `[microdeposit amount 2]`'),
        'description': ('Enable a node to send funds by verifying correct '
                        'microdeposit amounts:')
    },
    'whoami': {
        'function_name': whoami,
        'example': '@synapse whoami',
        'description': 'Return basic information about the Synapse user:'
    }
}


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
