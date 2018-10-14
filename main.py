import argparse

from init import create_bot
from common.texts import bot_name
from common.utils.logging_tools import get_logger
from common.utils.socket_app_lock import SocketAppLock


def main():
    logger = get_logger()
    if not __debug__:
        lock_name = "python-telegram-bot.main.lock"
        app_lock = SocketAppLock(lock_name, logger)
        if not app_lock.lock():
            print(f"The bot already has been started or did not shutdown correctly. "
                  f"Please stop the running bot / remove the {lock_name} file.")
            return
    args = get_args()
    bot = create_bot(args.admin_id)
    bot.run(args.token)
    if not __debug__:
        app_lock.unlock()


def get_args():
    parser = argparse.ArgumentParser(description=f"Run the {bot_name} for Telegram.")
    parser.add_argument('-t', dest="token", required=True, help='Your Telegram API token')
    parser.add_argument('-a', dest="admin_id", type=int, required=False, help='The admin user\'s Telegram ID')
    return parser.parse_args()


if __name__ == '__main__':
    main()
