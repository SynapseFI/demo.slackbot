"""Commands that can be called by Synapse slackbot."""
import datetime
import os
from synapse_pay_rest import Client, Node, Transaction
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


def whoami(slack_user_id, params):
    """Return info on the user.

    TODO:
        - should not choke if the user isn't registered yet
    """
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    return 'You are {0} (user_id: {1})'.format(synapse_user.legal_names[0],
                                               synapse_user.id)


def register(slack_user_id, params):
    """Create a new user with Synapse.

    TODO:
        - accept these as separate msgs instead of | delimited (?)
        - don't let a user register more than once
    """
    # these 'options' are actually required for the lib to work until pending
    #   API update or lib change.
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
    # add to db
    user = User(slack_user_id, synapse_user.id)
    db.session.add(user)
    db.session.commit()
    return 'User created - {0} (user_id: {1})'.format(synapse_user.legal_names[0],
                                                      synapse_user.id)


def add_cip(slack_user_id, params):
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
    user = doc.user
    return ('Base document (document_id: {0}) added for {1} (user_id: {2})'.format(
            doc.id, name, user.id))
"""
file upload format:

[{'type': 'message', 'bot_id': None, 'user': 'U2SLBSK9P', 'file': {'filetype': 'png', 'groups': [], 'comments_count': 0, 'original_w': 598, 'name': 'Screen Shot 2016-11-01 at 1.50.44 PM.png', 'user': 'U2SLBSK9P', 'thumb_480_h': 310, 'timestamp': 1478052943, 'image_exif_rotation': 1, 'size': 81556, 'original_h': 386, 'thumb_480_w': 480, 'thumb_360_w': 360, 'thumb_160': 'https://files.slack.com/files-tmb/T2SJGSJF5-F2XAHJ32S-84566533b9/screen_shot_2016-11-01_at_1.50.44_pm_160.png', 'id': 'F2XAHJ32S', 'thumb_80': 'https://files.slack.com/files-tmb/T2SJGSJF5-F2XAHJ32S-84566533b9/screen_shot_2016-11-01_at_1.50.44_pm_80.png', 'thumb_360_h': 232, 'is_external': False, 'ims': [], 'channels': ['C2SL02UNL'], 'title': 'Screen Shot 2016-11-01 at 1.50.44 PM.png', 'pretty_type': 'PNG', 'mode': 'hosted', 'display_as_bot': False, 'permalink_public': 'https://slack-files.com/T2SJGSJF5-F2XAHJ32S-1c999ff7fb', 'editable': False, 'is_public': True, 'mimetype': 'image/png', 'thumb_360': 'https://files.slack.com/files-tmb/T2SJGSJF5-F2XAHJ32S-84566533b9/screen_shot_2016-11-01_at_1.50.44_pm_360.png', 'permalink': 'https://slackbot-sandbox.slack.com/files/steven/F2XAHJ32S/screen_shot_2016-11-01_at_1.50.44_pm.png', 'public_url_shared': False, 'url_private_download': 'https://files.slack.com/files-pri/T2SJGSJF5-F2XAHJ32S/download/screen_shot_2016-11-01_at_1.50.44_pm.png', 'username': '', 'url_private': 'https://files.slack.com/files-pri/T2SJGSJF5-F2XAHJ32S/screen_shot_2016-11-01_at_1.50.44_pm.png', 'thumb_480': 'https://files.slack.com/files-tmb/T2SJGSJF5-F2XAHJ32S-84566533b9/screen_shot_2016-11-01_at_1.50.44_pm_480.png', 'thumb_64': 'https://files.slack.com/files-tmb/T2SJGSJF5-F2XAHJ32S-84566533b9/screen_shot_2016-11-01_at_1.50.44_pm_64.png', 'external_type': '', 'created': 1478052943}, 'upload': True, 'display_as_bot': False, 'subtype': 'file_share', 'team': 'T2SJGSJF5', 'username': '<@U2SLBSK9P|steven>', 'ts': '1478052946.000180', 'text': '<@U2SLBSK9P|steven> uploaded a file: <https://slackbot-sandbox.slack.com/files/steven/F2XAHJ32S/screen_shot_2016-11-01_at_1.50.44_pm.png|Screen Shot 2016-11-01 at 1.50.44 PM.png>', 'channel': 'C2SL02UNL'}]
"""


def add_physical_doc(slack_user_id, params):
    """Upload a physical doc for user's CIP."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    base_doc = synapse_user.base_documents[-1]
    base_doc.add_physical_document()


def add_virtual_doc(slack_user_id, params):
    """Add a virtual doc for user's CIP."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    base_doc = synapse_user.base_documents[-1]
    virtual_doc = base_doc.add_virtual_document(type='SSN', value=params)
    return ('SSN doc (id: {0}) added to base document (id: {1}) for {2} (user_id: {3})'.format(
            virtual_doc.id, base_doc.id, synapse_user.legal_names[0], synapse_user.id))


def list_resource(slack_user_id, params):
    """List the specified resource (node/transaction)."""
    if params.startswith('nodes'):
        return list_nodes(slack_user_id)
    elif params.startswith('transactions'):
        from_id = word_after(params, 'from')
        return list_transactions(slack_user_id, from_id)


def list_nodes(slack_user_id):
    """Return the user's Synapse nodes."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    nodes = Node.all(user=synapse_user)
    formatted = ['{0} - {1} (node_id: {2})'.format(node.type,
                                                   node.nickname,
                                                   node.id)
                 for node in nodes]
    if formatted:
        return '\n'.join(formatted)
    else:
        return 'No nodes found for {0} (user_id: {1})'.format(synapse_user.legal_names[0],
                                                              synapse_user.id)


def list_transactions(slack_user_id, from_id):
    """Return the user's Synapse transactions."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    node = Node.by_id(user=synapse_user, id=from_id)
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
    if formatted:
        return '\n'.join(formatted)
    else:
        return 'No transactions found for node_id: {0})'.format(node.id)


def send(slack_user_id, params):
    """Create a Synapse transaction."""
    synapse_user = synapse_user_from_slack_user_id(slack_user_id)
    from_node_id = word_after(params, 'from')
    from_node = Node.by_id(user=synapse_user, id=from_node_id)
    args = {
        'amount': word_after(params, 'send'),
        'to_id': word_after(params, 'to'),
        'to_type': 'SYNAPSE-US',
        'currency': 'USD',
        'ip': '127.0.0.1'
    }
    if 'on' in params:
        args['process_in'] = word_after(params, 'in')
    transaction = Transaction.create(from_node, **args)
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
