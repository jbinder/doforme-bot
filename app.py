import logging
import os
from flask import Flask, request
from telegram import Update

from components.feedback.feedback_component import FeedbackComponent
from do_for_me_bot import DoForMeBot
from services.task_service import TaskService
from services.telegram_service import TelegramService
from services.user_service import UserService
from texts import texts, bot_name


def get_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    return logging.getLogger(__name__)


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
    logger = get_logger()
    user_service = UserService()
    task_service = TaskService()
    telegram_service = TelegramService(user_service)
    components = {'feedback': FeedbackComponent(admin_id)}
    bot = DoForMeBot(bot_name, texts, telegram_service, task_service, user_service, components,
                     admin_id, logger)
    update_queue, bot_instance = bot.run(token, 'https://{}/{}'.format(dns, secret))
    application.run(host=ip, port=port)
