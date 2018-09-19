import argparse
import logging

from do_for_me_bot import DoForMeBot
from services.feedback_service import FeedbackService
from services.task_service import TaskService
from services.telegram_service import TelegramService
from services.user_service import UserService
from texts import texts, bot_name
from utils.app_lock import AppLock


def main():
    logger = get_logger()
    lock_name = "main.lock"
    app_lock = AppLock(lock_name, logger)
    if not app_lock.lock():
        print(f"The bot already has been started or did not shutdown correctly. "
              f"Please stop the running bot / remove the {lock_name} file.")
        return
    args = get_args()
    user_service = UserService()
    task_service = TaskService()
    telegram_service = TelegramService(user_service)
    feedback_service = FeedbackService()
    bot = DoForMeBot(bot_name, texts, telegram_service, task_service, user_service, feedback_service,
                     args.admin_id, logger)
    bot.run(args.token)
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
