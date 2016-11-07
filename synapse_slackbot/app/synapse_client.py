import os
from synapse_pay_rest import Client

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
