from .commands import list_nodes, list_transactions, send, verify_node, whoami


COMMANDS = {
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
