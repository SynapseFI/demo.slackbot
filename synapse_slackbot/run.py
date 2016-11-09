#!/usr/bin/env python3
"""Start event loop."""
import time
import os
import _thread
from flask import render_template, request
from synapse_pay_rest import User as SynapseUser
from synapse_pay_rest.models.nodes import AchUsNode, SynapseUsNode
from .config import app, db, slack_client
from .app.synapse_bot import SynapseBot
from .synapse_client import synapse_client
from .models import User

synapse_bot = SynapseBot(slack_client, os.environ.get('SLACKBOT_ID'))


@app.route('/register/<slack_id>', methods=['GET', 'POST'])
def register(slack_id):
    if request.method == 'GET':
        return render_template('register.html', slack_id=slack_id)
    elif request.method == 'POST':
        process_form(slack_id, request)


def process_form(slack_id, request):
    synapse_user = create_synapse_user(slack_id, request)
    submit_cip(synapse_user, request)
    debit_node = create_debit_node(synapse_user, request)
    savings_node = create_savings_node(synapse_user, request)
    create_user(slack_id, synapse_user.id, debit_node.id, savings_node.id)


def create_synapse_user(slack_id, form_data):
    # these 'options' actually required until pending API update or lib change
    options = {
        'note': 'created by Synapse Slackbot',
        'supp_id': slack_id,
        'is_business': False,
        'cip_tag': 1
    }
    synapse_user = SynapseUser.create(client=synapse_client,
                                      email=request.form['email'],
                                      phone_number=request.form['phone'],
                                      legal_name=request.form['name'].title(),
                                      **options)
    return synapse_user


def submit_cip(synapse_user, request):
    year, month, day = request.form['birthday'].split('-')
    base_doc = synapse_user.add_base_document(
        ip='127.0.0.1',
        name=request.form['name'],
        alias=request.form['name'],
        birth_day=int(day),
        birth_month=int(month),
        birth_year=int(year),
        email=request.form['email'],
        phone_number=request.form['phone'],
        entity_type='NOT_KNOWN',
        entity_scope='Not Known',
        address_street=request.form['address_street'],
        address_city=request.form['address_city'],
        address_subdivision=request.form['address_state'].upper(),
        address_postal_code=request.form['address_zip'],
        address_country_code='US')
    v_doc = base_doc.add_virtual_document(type='SSN',
                                          value=request.form['ssn'])
    img_file = request.files['govt_id']
    p_doc = base_doc.add_physical_document(type='GOVT_ID',
                                           mime_type='image/jpeg',
                                           byte_stream=img_file.read())


def create_debit_node(synapse_user, request):
    return AchUsNode.create(
        synapse_user,
        account_number=request.form['account_number'],
        routing_number=request.form['routing_number'],
        nickname='Synapse Automatic Savings Debit Account',
        account_type='PERSONAL',
        account_class='CHECKING'
    )


def create_savings_node(synapse_user, form_data):
    return SynapseUsNode.create(synapse_user,
                                nickname='Synapse Automatic Savings Account')


def create_user(slack_id, synapse_id, debit_node, savings_node):
    user = User(slack_id, synapse_id, debit_node_id, savings_node_id)
    db.session.add(user)
    db.session.commit()


def startEventLoop():
    # second delay between reading from Slack RTM firehose
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print('SynapseBot connected and running!')
        while True:
            stream = synapse_bot.slack_client.rtm_read()
            print(stream)
            if stream and len(stream) > 0:
                synapse_bot.parse_slack_output(stream)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed.')

if __name__ == '__main__':
    app.run()
    _thread.start_new_thread(startEventLoop, ())
