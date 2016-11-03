"""Commands that can be called by Synapse slackbot."""
import datetime
import os
from synapse_pay_rest import Client, Node, Transaction
from synapse_pay_rest.models.nodes import AchUsNode
from synapse_pay_rest import User as SynapseUser
from db_config import db
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
    """Create a new user with Synapse.

    TODO:
        - accept these as separate msgs instead of | delimited (?)
        - don't let a user register more than once
    """
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
                                      legal_name=params['name'],
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
    return user_summary(synapse_user)


def add_base_doc(slack_user_id, params):
    """Add Synapse CIP base document to user."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    name = synapse_user.legal_names[0]
    day, month, year = bday_string_to_ints(params['dob'])
    doc = synapse_user.add_base_document(
        ip=server_ip,
        name=name,
        alias=name,
        birth_day=day,
        birth_month=month,
        birth_year=year,
        email=synapse_user.logins[0]['email'],
        phone_number=synapse_user.phone_numbers[0],
        entity_type='NOT_KNOWN',
        entity_scope='Not Known',
        address_street=params['street'],
        address_city=params['city'],
        address_subdivision=params['state'],
        address_postal_code=params['zip'],
        address_country_code='US'
    )
    synapse_user = doc.user
    return ('Base document added.\n' + user_summary(synapse_user))


def add_physical_doc(slack_user_id, params):
    """Upload a physical doc for user's CIP."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    base_doc = synapse_user.base_documents[-1]
    physical_doc = base_doc.add_physical_document(type='GOVT_ID', url=params)
    synapse_user = physical_doc.base_document.user
    return ('*GOVT_ID added.*\n' + user_summary(synapse_user))


def add_virtual_doc(slack_user_id, params):
    """Add a virtual doc for user's CIP."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    base_doc = synapse_user.base_documents[-1]
    virtual_doc = base_doc.add_virtual_document(type='SSN', value=params)
    synapse_user = virtual_doc.base_document.user
    return ('*SSN added.*\n' + user_summary(synapse_user))


def add_node(slack_user_id, params):
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    node = AchUsNode.create(synapse_user,
                            nickname=params['nickname'],
                            account_number=params['account'],
                            routing_number=params['routing'],
                            account_type='PERSONAL',
                            account_class=params['type'].upper())
    return ('*Node added.*\n' + node_summary(node))


def verify_node(slack_user_id, params):
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    id = first_word(params)
    node = Node.by_id(user=synapse_user, id=id)
    amount1 = word_after(params, id)
    amount2 = word_after(params, amount1)
    node = node.verify_microdeposits(amount1=amount1, amount2=amount2)
    return ('*Node verified.*\n' + node_summary(node))


def list_nodes(slack_user_id, params):
    """Return the user's Synapse nodes."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    nodes = Node.all(user=synapse_user)
    if nodes:
        return '\n'.join([node_summary(node) for node in nodes])
    else:
        return '*No nodes found for user.*'


def list_transactions(slack_user_id, params):
    """Return the user's Synapse transactions."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    node = Node.by_id(user=synapse_user, id=word_after(params, 'from'))
    transactions = Transaction.all(node=node)
    if transactions:
        return '\n'.join([transaction_summary(trans) for trans in transactions])
    else:
        return '*No transactions found for node.*'.format(node.id)


def send(slack_user_id, params):
    """Create a Synapse transaction."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    from_node_id = word_after(params, 'from')
    from_node = Node.by_id(user=synapse_user, id=from_node_id)
    args = {
        'amount': first_word(params),
        'to_id': word_after(params, 'to'),
        'to_type': 'ACH-US',
        'currency': 'USD',
        'ip': server_ip
    }
    if 'on' in params:
        args['process_in'] = word_after(params, 'in')
    transaction = Transaction.create(from_node, **args)
    return ('*Transaction created.*\n' + transaction_summary(transaction))


# helpers
def synapse_user_from_slack_user_id(slack_user_id):
    """Find user's synapse id and get the Synapse user."""
    user = User.query.filter(User.slack_user_id==slack_user_id).all()[-1]
    return SynapseUser.by_id(client=synapse_client, id=user.synapse_user_id)


def format_currency(amount):
    """Convert float to string currency with 2 decimal places."""
    str_format = str(amount)
    cents = str_format.split('.')[1]
    if len(cents) == 1:
        str_format += '0'
    return str_format


def first_word(sentence):
    return sentence.split(' ', 1)[0]


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


def bday_string_to_ints(bday):
    """Split mm/dd/yy(yy) into separate m, d, and y fields."""
    month, day, year = [int(num) for num in bday.split('/')]
    return (month, day, year)


def user_summary(synapse_user):
    return ('```'
            'Synapse user details:\n'
            'user id: {0}\n'.format(synapse_user.id) +
            'name: {0}\n'.format(synapse_user.legal_names[0]) +
            'permissions: {0}\n'.format(synapse_user.permission) +
            '```')


def node_summary(node):
    return ('```'
            'Synapse node details:\n'
            'node id: {0}\n'.format(node.id) +
            'nickname: {0}\n'.format(node.nickname) +
            'type: {0}\n'.format(node.account_class) +
            'permissions: {0}\n'.format(node.permission) +
            '```')


def transaction_summary(trans):
    return('```'
           'Synapse transaction details:\n'
           'trans id: {0}\n'.format(trans.id) +
           'from node id: {0}\n'.format(trans.node.id) +
           'to name: {0}\n'.format(trans.to_info['user']['legal_names'][0]) +
           'to node id: {0}\n'.format(trans.to_id) +
           'amount: {0}\n'.format(format_currency(trans.amount)) +
           'status: {0}\n'.format(trans.recent_status['note']) +
           'created_on: {0}\n'.format(timestamp_to_string(trans.created_on)) +
           'process on: {0}\n'.format(timestamp_to_string(trans.process_on)) +
           '```')
