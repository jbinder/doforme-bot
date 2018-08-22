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


def do(bot, update, user_data):
    text = update.message.text[len("/do"):].strip()
    if text == "@DoForMeBot" or not text:
        update.message.reply_text(
            f"Please include a task title, {update.effective_user.first_name}!\n")
        return ConversationHandler.END

    user_data['title'] = text

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=user_name, callback_data=user_id)]
         for (user_id, user_name) in get_chat_users(bot, update.message.chat.id)],
        one_time_keyboard=True)
    update.message.reply_text(
        f"Whom do you want to enslave doing {user_data['title']} for you, {update.effective_user.first_name}?\n"
        f"Select below!",
        reply_markup=markup, quote=False)

    return ConversationHandler.END


def shrug(bot, update, user_data):
    update.message.reply_text("¯\_(ツ)_/¯")


def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def new_chat_member(bot, update):
    chat_id = update.message.chat.id
    for member in update.message.new_chat_members:
        register_user(chat_id, member, update)
    if len(update.message.new_chat_members) < 1:
        register_user(chat_id, update.effective_user, update)
# TODO: if it is the bot itself, send greeting and instructions (existing users need to say hello)


def register_user(chat_id, member, update):
    if chat_id not in state['users']:
        state['users'][chat_id] = []
    if member.id not in state['users'][chat_id]:
        update.message.reply_text(
            f"Welcome in the {update.message.chat.title}'s realm of productivity, "
            f"{member.first_name}! Use"
            f"\n\n/do [your task title]\n\nto start distributing tasks to your helpful peers!\n")
        state['users'][chat_id].append(member.id)


def left_chat_member(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.left_chat_member.id
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
    # TODO: append if exists
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
        entry_points=[CommandHandler('do', do, pass_user_data=True)],
        states={
        },
        fallbacks=[RegexHandler('^.*$', shrug, pass_user_data=True)],
        per_chat=True,
        per_user=True,
    )
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))
    dp.add_handler(CallbackQueryHandler(callback, pass_user_data=True))

    dp.add_handler(MessageHandler(Filters.text, new_chat_member))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
