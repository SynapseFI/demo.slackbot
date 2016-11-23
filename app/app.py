import time
import os
import _thread
import traceback
import sys
from flask import jsonify, render_template, request
from synapse_pay_rest.errors import SynapsePayError
from config import app, slack_client
from synapse_bot import SynapseBot
from models import User


@app.route('/')
def index():
    return 'Flask is running!'


@app.route('/register/<slack_id>', methods=['GET', 'POST'])
def register(slack_id):
    """Route for handling user registration form."""
    if request.method == 'GET':
        return render_template('register.html', slack_id=slack_id)
    elif request.method == 'POST':
        if User.from_slack_id(slack_id):
            response = jsonify({
                'message': 'You are already registered with this Slack ID.'
            })
            response.status_code = 409
            return response
        try:
            User.from_request(slack_id, request)
            response = jsonify({
                'message': 'You are now registered. Invite Synapsebot to a '\
                           'Slack channel and say "@synapse help".'
            })
            response.status_code = 200
        except SynapsePayError as e:
            response = jsonify({
                'message': 'API error: {0}'.format(e.message)
            })
            response.status_code = e.response.status_code
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            response = jsonify({
                'message': 'Server error: {0}'.format(sys.exc_info()[1])
            })
            response.status_code = 500
        return response


def start_bot_event_loop():
    """Main event loop for program."""
    synapse_bot = SynapseBot(slack_client, os.environ.get('SLACKBOT_ID'))
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
    port = int(os.environ.get('PORT', 5000))
    _thread.start_new_thread(start_bot_event_loop, ())
    app.run(host='0.0.0.0', port=port)
