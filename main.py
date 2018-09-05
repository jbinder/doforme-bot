import argparse
import logging

from do_for_me_bot import DoForMeBot
from services.task_service import TaskService
from services.telegram_service import TelegramService
from services.user_service import UserService
from texts import texts, bot_name


def main():
    args = get_args()
    user_service = UserService()
    task_service = TaskService()
    telegram_service = TelegramService(user_service)
    bot = DoForMeBot(bot_name, texts, telegram_service, task_service, user_service, get_logger())
    bot.run(args.token)


def get_args():
    parser = argparse.ArgumentParser(description=f"Run the {bot_name} for Telegram.")
    parser.add_argument('-t', dest="token", required=True, help='Your Telegram API token')
    return parser.parse_args()


def get_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


if __name__ == '__main__':
    main()
