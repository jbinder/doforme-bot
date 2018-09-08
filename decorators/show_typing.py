from telegram import Bot, Update, ChatAction


def show_typing(f):
    def decorator(*args, **kw):
        bot = args[1]
        update = args[2]
        if not isinstance(bot, Bot):
            raise RuntimeError("Unable to attach decorator as the second argument is not a bot object!")
        if not isinstance(update, Update):
            raise RuntimeError("Unable to attach decorator as the third argument is not an update object!")
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        return f(*args, **kw)

    return decorator
