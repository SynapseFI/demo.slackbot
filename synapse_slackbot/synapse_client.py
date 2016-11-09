"""Initializes the SynapsePayRest client for making SynapsePay API calls."""
import os
from synapse_pay_rest import Client

# initialize synapse client
synapse_client = Client(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    fingerprint=os.environ['FINGERPRINT'],
    ip_address='127.0.0.1',
    logging=True,
    development_mode=True
)
