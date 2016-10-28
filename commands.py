"""Command logic for the slackbot."""
import datetime
import os
from synapse_pay_rest import Client, User, Node, Transaction


# synapse_pay_rest config
client = Client(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    fingerprint=os.environ['FINGERPRINT'],
    ip_address='127.0.0.1',
    logging=True,
    development_mode=True
)

SYNAPSE_USER_ID = '57d2055a86c27339ffdee4cc'
user = User.by_id(client=client, id=SYNAPSE_USER_ID)


# bot commands
class Commands():
    """General commands for Synapse slackbot."""
    @staticmethod
    def who_am_i(command):
        """Return info on the user."""
        return 'You are {0} (user_id: {1})'.format(user.legal_names[0], user.id)

    @staticmethod
    def list_resource(command):
        """List the specified resource (node/transaction)."""
        resource = Commands.word_after(command, 'list')
        if resource == 'nodes':
            return Commands.list_nodes()
        elif resource == 'transactions':
            from_id = word_after(command, 'from')
            return Commands.list_transactions(from_id)

    @staticmethod
    def list_nodes():
        """Return the user's Synapse nodes."""
        nodes = Node.all(user=user)
        formatted = ['{0} - {1} (node_id: {2})'.format(node.type,
                                                       node.nickname,
                                                       node.id)
                     for node in nodes]
        return '\n'.join(formatted)

    @staticmethod
    def list_transactions(from_id):
        """Return the user's Synapse transactions."""
        node = Node.by_id(user=user, id=from_id)
        transactions = Transaction.all(node=node)
        formatted = ["You sent {0} on {1} to {2}'s {3} node (trans_id: {4}).".format(
                            format_currency(trans.amount),
                            timestamp_to_string(trans.process_on),
                            trans.to_info['user']['legal_names'][0],
                            trans.to_info['type'],
                            trans.id
                        )
                     for trans in transactions]
        return '\n'.join(formatted)

    @staticmethod
    def send(command):
        """Create a Synapse transaction."""
        from_node_id = Commands.word_after(command, 'from')
        from_node = Node.by_id(user=user, id=from_node_id)
        args = {
            'amount': Commands.word_after(command, 'send'),
            'to_id': Commands.word_after(command, 'to'),
            'to_type': 'SYNAPSE-US',
            'currency': 'USD',
            'ip': '127.0.0.1'
        }
        if 'on' in command:
            args['process_in'] = Commands.word_after(command, 'in')
        try:
            transaction = Transaction.create(from_node, **args)
        except Exception as e:
            print(e.__dict__)
        return (
            "Created ${0} transaction from {1}'s {2} node to {3}'s {4} node.\n"
            "Scheduled for {5}.\nCurrent status: {6}.".format(
                Commands.format_currency(transaction.amount),
                transaction.from_info['user']['legal_names'][0],
                transaction.from_info['type'],
                transaction.to_info['user']['legal_names'][0],
                transaction.to_info['type'],
                Commands.timestamp_to_string(transaction.process_on),
                transaction.recent_status['note']
            )
        )

    @staticmethod
    def register(command):
        """Create a new user with Synapse."""

    # helpers
    @staticmethod
    def format_currency(amount):
        """Convert float to string currency with 2 decimal places."""
        str_format = str(amount)
        cents = str_format.split('.')[1]
        if len(cents) == 1:
            str_format += '0'
        return str_format

    @staticmethod
    def word_after(sentence, word):
        """Return the word following the given word in the sentence string."""
        words = sentence.split()
        index = words.index(word) + 1
        return words[index]

    @staticmethod
    def timestamp_to_string(timestamp):
        """Convert a 13-digit UNIX timestamp to a formatted datetime string."""
        without_ms = int(str(timestamp)[:-3])
        timestamp = datetime.datetime.fromtimestamp(without_ms)
        return timestamp.strftime('%Y-%m-%d')
