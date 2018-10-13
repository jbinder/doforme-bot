import os
from flask import Flask, request
from telegram import Update

from init import create_bot

ip = os.environ['DFM_WEB_IP']
port = int(os.environ['DFM_WEB_PORT'])
dns = os.environ['DFM_WEB_DNS']
token = os.environ['DFM_BOT_TOKEN']
secret = os.environ['DFM_REQUEST_SECRET']
admin_id = int(os.environ['DFM_ADMIN_ID'])

application = Flask(__name__)


@application.route('/')
def home():
    return 'Up.'


@application.route('/' + secret, methods=['GET', 'POST'])
def webhook():
    if request.json:
        update_queue.put(Update.de_json(request.json, bot_instance))
    return ''


if __name__ == '__main__':
    bot = create_bot(admin_id)
    update_queue, bot_instance = bot.run(token, 'https://{}/{}'.format(dns, secret))
    application.run(host=ip, port=port)
