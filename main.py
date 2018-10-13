import argparse
import logging

from components.feedback.feedback_component import FeedbackComponent
from components.user.user_component import UserComponent
from do_for_me_bot import DoForMeBot
from services.task_service import TaskService
from services.telegram_service import TelegramService
from components.user.user_service import UserService
from texts import texts, bot_name
from utils.socket_app_lock import SocketAppLock


def main():
    logger = get_logger()
    if not __debug__:
        lock_name = "doforme.doforme-bot.main.lock"
        app_lock = SocketAppLock(lock_name, logger)
        if not app_lock.lock():
            print(f"The bot already has been started or did not shutdown correctly. "
                  f"Please stop the running bot / remove the {lock_name} file.")
            return
    args = get_args()
    user_service = UserService()  # TODO: get from component
    task_service = TaskService()
    telegram_service = TelegramService(user_service)
    components = {
        'feedback': FeedbackComponent(args.admin_id),
        'user': UserComponent(args.admin_id, bot_name)
    }
    bot = DoForMeBot(bot_name, texts, telegram_service, task_service, components, args.admin_id, logger)
    bot.run(args.token)
    if not __debug__:
        app_lock.unlock()


def get_args():
    parser = argparse.ArgumentParser(description=f"Run the {bot_name} for Telegram.")
    parser.add_argument('-t', dest="token", required=True, help='Your Telegram API token')
    parser.add_argument('-a', dest="admin_id", type=int, required=False, help='The admin user\'s Telegram ID')
    return parser.parse_args()


def get_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


if __name__ == '__main__':
    main()
