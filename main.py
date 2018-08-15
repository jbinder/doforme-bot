import argparse
import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, ConversationHandler, CommandHandler, RegexHandler, MessageHandler, Filters, \
    CallbackQueryHandler

TITLE, USER = range(2)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

state = {
    'users': {},
    'tasks': {},
}


def get_args():
    parser = argparse.ArgumentParser(description='Run the DoForMe-Bot for Telegram.')
    parser.add_argument('-t', dest="token", required=True, help='Your Telegram API token')
    return parser.parse_args()


def get_chat_users(bot, chat_id):
    return [(user_id, bot.getChatMember(chat_id, user_id).user.name) for user_id in state['users'][chat_id]]


def do(bot, update):
    update.message.reply_text(
        f"What is thy request, {update.effective_user.first_name}?",
        quote=False)

    return TITLE


def title(bot, update, user_data):
    user_data['title'] = update.message.text

    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=user_name, callback_data=user_id)] for (user_id, user_name) in get_chat_users(bot, update.message.chat.id)], one_time_keyboard=True)
    update.message.reply_text(
        f"Whom do you want to enslave doing {user_data['title']} for you, {update.effective_user.first_name}?",
        reply_markup=markup, quote=False)

    return USER


def shrug(bot, update, user_data):
    update.message.reply_text("¯\_(ツ)_/¯")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def new_chat_member(bot, update):
    chat_id = update.message.chat.id
    for member in update.message.new_chat_members:
        update.message.reply_text(
            f"Welcome in the {update.message.chat.title}'s realm of productivity, "
            f"{member.first_name}!\n"
            f"Use /do to start distributing tasks to your helpful peers!")
        if chat_id not in state['users']:
            state['users'][chat_id] = []
        state['users'][chat_id].append(member.id)


def left_chat_member(bot, update):
    chat_id = update.message.chat_id
    user_id = update.left_chat_member.id
    if chat_id in state['users'] and user_id in state['users'][chat_id]:
        state['users'][chat_id].remove(user_id)
        update.message.reply_text(
            f"Farewell, my dear little exhausted busy bee {update.left_chat_member.first_name}!")


def callback(bot, update, user_data):
    user_id = update.callback_query.data
    user_data['user_id'] = user_id
    user_name = bot.getChatMember(update.callback_query.message.chat.id, user_id).user.name
    if user_id not in state['tasks']:
        state['tasks'][user_id] = []
    state['tasks'][user_id].append(user_data)
    update.callback_query.message.reply_text(
        f"I burdened {user_name} with your request to {user_data['title']}.",
        quote=False)
    update.callback_query.answer()


def main():
    args = get_args()
    updater = Updater(args.token)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('do', do)],
        states={
            TITLE: [MessageHandler(Filters.text, title, pass_user_data=True)],
        },
        fallbacks=[RegexHandler('^.*$', shrug, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))
    dp.add_handler(CallbackQueryHandler(callback, pass_user_data=True))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
