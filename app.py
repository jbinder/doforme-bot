import os
from flask import Flask, request
from pony.orm import db_session
from telegram import Update

from common.utils.db_tools import init_database, get_database
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
    is_up = True
    # noinspection PyBroadException
    try:
        db = get_database()
        init_database(db)
        with db_session:
            if not db.get_connection():
                is_up = False
    except Exception:
        is_up = False

    return 'Up.' if is_up else 'Down.'


@application.route('/' + secret, methods=['GET', 'POST'])
def webhook():
    if request.json:
        update_queue.put(Update.de_json(request.json, bot_instance))
    return ''


if __name__ == '__main__':
    bot = create_bot(admin_id)
    update_queue, bot_instance = bot.run(token, 'https://{}/{}'.format(dns, secret))
    application.run(host=ip, port=port)
