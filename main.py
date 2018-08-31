import argparse
import logging

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler

# USER = range(1)
from libraries.telegramcalendar import telegramcalendar
from services.task_service import TaskService
from services.user_service import UserService

bot_name = "DoForMeBot"
texts = {'help': "Use\n"
                 f"/do [your task title] - to start distributing tasks to your helpful peers\n"
                 f"/tasks - to list your duties\n"
                 f"/help - to show this info\n"
                 f"Note: the do/tasks-commands only work in the private chat with the bot, not in groups!"}
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
user_service = UserService()
task_service = TaskService()


def get_args():
    parser = argparse.ArgumentParser(description=f"Run the {bot_name} for Telegram.")
    parser.add_argument('-t', dest="token", required=True, help='Your Telegram API token')
    return parser.parse_args()


def get_chat_users(bot, chat_id):
    return [(user_id, bot.getChatMember(chat_id, user_id).user.name)
            for user_id in user_service.get_chat_users(chat_id)]


def get_chats(bot, user_id):
    chats = []
    for chat_id in user_service.get_chats_of_user(user_id):
        chats.append((chat_id, bot.getChat(chat_id).title))
    return chats


def select_chat(bot, update, user_data):
    if not assure_private_chat(update):
        return

    text = update.message.text[len("/do"):].strip()
    if text == "@DoForMeBot" or not text:
        update.message.reply_text(
            f"Please include a task title, {update.effective_user.first_name}!\n")
        return

    user_data['title'] = text
    user_data['owner_id'] = update.effective_user.id

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=chat_name, callback_data=f"chat_id:{chat_id}")]
         for (chat_id, chat_name) in get_chats(bot, update.effective_user.id)])
    update.message.reply_text(
        f"Which is the place of power?\n"
        f"Select below!",
        reply_markup=markup, quote=False)


def select_user(bot, message, user_data):
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=user_name, callback_data=f"user_id:{user_id}")]
         for (user_id, user_name) in get_chat_users(bot, user_data['chat_id'])],
        one_time_keyboard=True)
    message.reply_text(
        f"Whom do you want to enslave doing {user_data['title']} for you, {message.chat.first_name}?\n"
        f"Select below!",
        reply_markup=markup, quote=False)


def select_due(bot, message, user_data):
    message.reply_text("Select a due date! ",
                        reply_markup=telegramcalendar.create_calendar())


def add_task(bot, message, user_data):
    user_id = user_data['user_id']
    chat_id = user_data['chat_id']
    user_name = get_mention(bot, chat_id, user_id)
    task_service.add_task(user_data)
    # TODO: append if exists
    message.reply_text(
        f"I burdened {user_name} with your request to {user_data['title']}.",
        quote=False, parse_mode=telegram.ParseMode.MARKDOWN)
    owner_user_name = get_mention(bot, message.chat.id, user_data['owner_id'])
    bot.send_message(
        chat_id,
        f"{owner_user_name} loaded {user_data['title']} on {user_name}'s back.",
        parse_mode=telegram.ParseMode.MARKDOWN)


def show_tasks(bot, update):
    if not assure_private_chat(update):
        return
    user_id = update.effective_user.id
    task_summary = get_task_summary(bot, user_id)
    tasks = task_service.get_tasks(user_id)
    markup = get_tasks_markup(tasks)
    update.message.reply_text(task_summary, reply_markup=markup)


# def set_reminder(bot, update):
#     if not assure_private_chat(update):
#         return
#     user_service.add_user_schedule_if_not_exists(update.effective_user.id, update.message.chat.id)
#     update.message.reply_text("You will now receive a daily overview of due tasks.")


def show_help(bot, update):
    update.message.reply_text(texts['help'])


# def shrug(bot, update, user_data):
#     update.message.reply_text("¯\_(ツ)_/¯")

def get_tasks_markup(tasks):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=f"Complete {task.title}", callback_data=f"complete:{task.id}")]
         for task in tasks if not task.done],
        one_time_keyboard=True)


def get_task_summary(bot, user_id):
    due_past = task_service.get_due_past(user_id)
    due_today = task_service.get_due_today(user_id)
    due_this_week = task_service.get_due_this_week(user_id)
    due_later_than_this_week = task_service.get_due_later_than_this_week(user_id)
    due_undefined = task_service.get_due_undefined(user_id)
    summary = (f"Overdue!!!!:\n{to_task_list(bot, due_past)}\n\n" if due_past else "") + \
              (f"Due today:\n{to_task_list(bot, due_today)}\n\n" if due_today else "") + \
              (f"This week:\n{to_task_list(bot, due_this_week)}\n\n" if due_this_week else "") + \
              (f"Later:\n{to_task_list(bot, due_later_than_this_week)}\n\n" if due_later_than_this_week else "") + \
              (f"Undefined:\n{to_task_list(bot, due_undefined)}\n\n" if due_undefined else "")
    return summary


def to_task_list(bot, due_tasks):
    return "\n".join([f"๏ {bot.getChat(task.chat_id).title}: {task.title} from "
                      f"{bot.getChatMember(task.chat_id, task.owner_id).user.name}"
                      for task in due_tasks])


def assure_private_chat(update):
    if update.message.chat.type != 'private':
        update.message.reply_text(f"Please switch to the private chat with @{bot_name} and write your commands there!")
        return False
    return True


def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def new_chat_member(bot, update):
    chat_id = update.message.chat.id
    for member in update.message.new_chat_members:
        register_user(chat_id, member, update)
        # TODO: if it is the bot itself, send greeting and instructions (existing users need to say hello)
    if len(update.message.new_chat_members) < 1:
        if update.effective_chat.type == "private":
            if len(get_chats(bot, update.effective_user.id)) < 1:
                update.message.reply_text("Please add the bot to a group to get started!")
            else:
                update.message.reply_text(texts['help'])
        else:
            register_user(chat_id, update.effective_user, update)


def register_user(chat_id, member, update):
    # TODO: only add if this is a group msesage!
    if user_service.add_user_chat_if_not_exists(member.id, chat_id):
        update.message.reply_text(
            f"Welcome in the {update.message.chat.title}'s realm of productivity, "
            f"{member.first_name}!\n\n" + texts['help'])


def left_chat_member(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.left_chat_member.id
    # TODO: delete tasks?
    if user_service.remove_user_chat_if_exists(user_id, chat_id):
        update.message.reply_text(
            f"Farewell, my dear little exhausted busy bee {update.message.left_chat_member.first_name}!")


def callback(bot, update, user_data):
    data = update.callback_query.data.split(":")
    if data[0] == "complete":
        task = task_service.get_task(data[1])
        task_service.complete_task(data[1])
        owner_name = get_mention(bot, task.chat_id, task.owner_id)
        user_name = get_mention(bot, task.chat_id, task.user_id)
        update.callback_query.message.reply_text(
            f"I released you from the task {task.title}.",
            quote=False)
        bot.send_message(
            task.chat_id,
            f"{owner_name}: {user_name} completed {task.title}!",
            parse_mode=telegram.ParseMode.MARKDOWN)
    elif len(data) > 1:
        user_data[data[0]] = int(data[1])
        if "user_id" not in user_data:
            select_user(bot, update.callback_query.message, user_data)
        elif "due" not in user_data:
            select_due(bot, update.callback_query.message, user_data)
        else:
            user_data.clear()
            raise RuntimeError("Invalid state, clearing input.")
    else:
        selected, date = telegramcalendar.process_calendar_selection(bot, update)
        if selected:
            user_data['due'] = date
            add_task(bot, update.callback_query.message, user_data)
            # bot.send_message(chat_id=update.callback_query.from_user.id,
            #                  text="You selected %s" % (date.strftime("%d/%m/%Y")),
            #                  reply_markup=ReplyKeyboardRemove())
            user_data.clear()

    update.callback_query.answer()


def show_all_task_overviews(bot, update):
    for user_id in user_service.get_all_users():
        task_summary = get_task_summary(bot, user_id)
        bot.send_message(user_id, task_summary)


def get_mention(bot, chat_id, user_id):
    user_name = bot.getChatMember(chat_id, user_id).user.name
    return f"[{user_name}](tg://user?id={user_id})"


# def inline_caps(bot, update, chat_data, user_data, update_queue):
#     query = update.inline_query.query
#     if not query:
#         return
#     results = list()
#     user_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text=user_name, callback_data=user_id)] for (user_id, user_name) in get_chat_users(bot, update.message.chat.id)], one_time_keyboard=True)
#     results.append(
#         InlineQueryResultArticle(
#             title=query,
#             reply_markup=user_keyboard,
#         )
#     )
#     bot.answer_inline_query(update.inline_query.id, InlineKeyboardMarkup([[InlineKeyboardButton("a", callback_data="a")]]))


def main():
    args = get_args()
    updater = Updater(args.token)
    dp = updater.dispatcher
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('do', select_chat, pass_user_data=True)],
    #     states={
    #         USER: [RegexHandler('^.*$', select_user, pass_user_data=True)]
    #     },
    #     fallbacks=[RegexHandler('^.*$', shrug, pass_user_data=True)],
    #     per_chat=True,
    #     per_user=True,
    # )
    # dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('do', select_chat, pass_user_data=True))
    dp.add_handler(CommandHandler('tasks', show_tasks))
    # dp.add_handler(CommandHandler('reminder', set_reminder))
    dp.add_handler(CommandHandler('help', show_help))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))
    dp.add_handler(CallbackQueryHandler(callback, pass_user_data=True))

    dp.add_handler(MessageHandler(Filters.text, new_chat_member))

    dp.job_queue.run_repeating(show_all_task_overviews, interval=60, first=0)

    # inline_caps_handler = InlineQueryHandler(inline_caps, pass_chat_data=True, pass_user_data=True, pass_update_queue=True)
    # dp.add_handler(inline_caps_handler)

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
