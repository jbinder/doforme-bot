import functools

from telegram import Bot, Update, ChatAction


def show_typing(f):
    @functools.wraps(f)
    def decorator(*args, **kw):
        bot = args[1]
        update = args[2]
        if not isinstance(bot, Bot):
            raise RuntimeError("Unable to attach decorator as the second argument is not a bot object!")
        if not isinstance(update, Update):
            raise RuntimeError("Unable to attach decorator as the third argument is not an update object!")
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        try:
            return f(*args, **kw)
        except Exception:
            bot.send_message(update.message.chat_id,
                             "Whoops, something happened... please try again or use /feedback to let us know.")
            raise

    return decorator
