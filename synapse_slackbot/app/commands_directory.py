from .commands import (add_base_doc, add_node, add_physical_doc,
                       add_virtual_doc, list_nodes, list_transactions,
                       register, send, verify_node, whoami)

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
