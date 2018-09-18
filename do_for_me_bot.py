from collections import Counter
from datetime import time, datetime, timedelta
from logging import Logger

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram.ext.jobqueue import Days

from decorators.show_typing import show_typing
from libraries.telegramcalendar import telegramcalendar
from services.feedback_service import FeedbackService
from services.task_service import TaskService
from services.telegram_service import TelegramService
from services.user_service import UserService


class DoForMeBot:
    bot_name: str
    texts: dict
    telegram_service: TelegramService
    task_service: TaskService
    user_service: UserService
    feedback_service: FeedbackService
    logger: Logger

    def __init__(self, bot_name, texts, telegram_service, task_service, user_service, feedback_service,
                 admin_id, logger):
        self.bot_name = bot_name
        self.texts = texts
        self.telegram_service = telegram_service
        self.task_service = task_service
        self.user_service = user_service
        self.feedback_service = feedback_service
        self.admin_id = admin_id
        self.logger = logger

    def run(self, token):
        updater = Updater(token)
        dp = updater.dispatcher

        cmd_handlers = [
            ('start', self._help_show, False),
            ('help', self._help_show, False),
            ('do', self._do_select_chat, True),
            ('tasks', self._tasks_show, False),
            ('stats', self._stats_show, False),
            ('feedback', self._feedback_add, False),
            ('admin-stats', self._admin_stats, False),
            ('admin-feedback-show', self._admin_feedback_show, False),
            ('admin-feedback-reply', self._admin_feedback_reply, False),
            ('admin-feedback-close', self._admin_feedback_close, False),
            ('admin-announce', self._admin_announce, False),
        ]
        [dp.add_handler(CommandHandler(command, callback, pass_user_data=pass_user_data))
         for command, callback, pass_user_data in cmd_handlers]

        msg_handlers = [
            (Filters.status_update.new_chat_members, self._chat_member_add),
            (Filters.status_update.left_chat_member, self._chat_member_remove),
            (Filters.text, self._chat_member_add)
        ]
        [dp.add_handler(MessageHandler(filters, callback)) for (filters, callback) in msg_handlers]

        dp.add_handler(CallbackQueryHandler(self._inline_handler, pass_user_data=True))

        jobs = [
            (self._job_daily_tasks_show_all, time(hour=5, minute=0)),
            (self._job_daily_tasks_show_daily, time(hour=11, minute=0)),
            (self._job_daily_tasks_show_daily, time(hour=17, minute=0)),
        ]
        [dp.job_queue.run_daily(callback, time=run_at) for (callback, run_at) in jobs]

        dp.job_queue.run_daily(self._job_weekly_review, time(hour=18, minute=0), days=(Days.SUN,))

        dp.add_error_handler(self._error_handler)

        updater.start_polling()
        updater.idle()

    @show_typing
    def _help_show(self, bot, update):
        update.message.reply_text(self.texts['help'])

    @show_typing
    def _do_select_chat(self, bot, update, user_data):
        user_data.clear()

        if not self._assure_private_chat(update):
            return

        text = update.message.text[len("/do"):].strip()
        if text == f"@{self.bot_name}" or not text:
            update.message.reply_text(self.texts['missing-title'](update.effective_user.first_name))
            return
        chats = self.telegram_service.get_chats(bot, update.effective_user.id)
        if len(chats) < 1:
            update.message.reply_text(self.texts['add-to-group'])
            return

        user_data['title'] = text
        user_data['owner_id'] = update.effective_user.id

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=chat_name, callback_data=f"chat_id:{chat_id}")]
             for (chat_id, chat_name) in chats])
        update.message.reply_text(self.texts['select-chat'], reply_markup=markup, quote=False)

    def _do_select_user(self, bot, message, user_data):
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=user_name, callback_data=f"user_id:{user_id}")]
             for (user_id, user_name) in self.telegram_service.get_chat_users(bot, user_data['chat_id'])],
            one_time_keyboard=True)
        message.reply_text(self.texts['select-user'](user_data['title'], message.chat.first_name),
                           reply_markup=markup, quote=False)

    def _do_select_due(self, bot, message, user_data):
        message.reply_text(self.texts['select-date'], reply_markup=telegramcalendar.create_calendar())

    def _do_add_task(self, bot, message, user_data):
        user_id = user_data['user_id']
        chat_id = user_data['chat_id']
        user_name = self.telegram_service.get_mention(bot, chat_id, user_id)
        self.task_service.add_task(user_data)
        message.reply_text(self.texts['added-task'](user_name, user_data['title']),
                           quote=False, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove())
        owner_user_name = self.telegram_service.get_mention(bot, message.chat.id, user_data['owner_id'])
        bot.send_message(chat_id, self.texts['added-task-to-group'](owner_user_name, user_name,
                                                                    user_data['title'],
                                                                    user_data['due']),
                         parse_mode=telegram.ParseMode.MARKDOWN)

    @show_typing
    def _tasks_show(self, bot, update):
        if not self.telegram_service.is_private_chat(update):
            update.message.reply_text(self._get_chat_tasks(bot, update.effective_chat.id))
            return

        user_id = update.effective_user.id
        tasks = [task for task in self.task_service.get_tasks(user_id) if not task.done]

        update.message.reply_text(f"{self.texts['task-headline-assigned']}:")
        if len(tasks) < 1:
            update.message.reply_text(self.texts['no-tasks'])

        for task in tasks:
            task_summary = self.texts['task-line-summary'](task, bot.getChat(task.chat_id).title,
                                                           bot.getChatMember(task.chat_id, task.owner_id).user.name)
            markup = self._get_task_markup(task)
            update.message.reply_text(task_summary, reply_markup=markup)

        tasks = [task for task in self.task_service.get_owning_tasks(user_id) if not task.done]
        text = f"{self.texts['task-headline-owning']}:\n"
        if len(tasks) < 1:
            text = text + self.texts['no-tasks']
        else:
            text = text + "\n".join(
                [self.texts['task-line-owning-summary'](task, bot.getChat(task.chat_id).title,
                                                        bot.getChatMember(task.chat_id, task.owner_id).user.name)
                 for task in tasks])
        update.message.reply_text(text)

    @show_typing
    def _stats_show(self, bot, update):
        if self.telegram_service.is_private_chat(update):
            stats = self.task_service.get_user_stats(update.effective_user.id)
            owning_message = self._get_stats_message(stats['owning'])
            assigned_message = self._get_stats_message(stats['assigned'])
            message = self.texts['task-stats'](stats['owning']['count'], owning_message,
                                               stats['assigned']['count'], assigned_message)
        else:
            stats = self.task_service.get_chat_stats(update.effective_chat.id)
            message = self._get_stats_message(stats)
        update.message.reply_text(message)

    @show_typing
    def _feedback_add(self, bot, update):
        text = update.message.text[len("/feedback"):].strip()
        if not text:
            update.message.reply_text(self.texts['missing-text'](update.effective_user.first_name))
            return
        self.feedback_service.add(update.effective_user.id, text)
        update.message.reply_text(self.texts['feedback-thanks'])
        if self.admin_id:
            bot.send_message(self.admin_id, self.texts['feedback-new'])

    @show_typing
    def _admin_stats(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        task_stats = self.task_service.get_all_stats()
        user_stats = self.user_service.get_stats()
        feedback_stats = self.feedback_service.get_stats()
        message = f"{self.texts['tasks']}:\n"
        message = message + self._get_stats_message(task_stats)
        message = message + f"\n\n{self.texts['users']}:\n" + "\n".join([f"{key}: {str(value)}" for
                                                                         key, value in user_stats.items()])
        message = message + f"\n\n{self.texts['feedback']}:\n" + "\n".join([f"{key}: {str(value)}"
                                                                            for key, value in feedback_stats.items()])
        update.message.reply_text(message)

    @show_typing
    def _admin_feedback_show(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        message = "\n".join([f"{feedback.id} / {feedback.created.date()} / {feedback.text}"
                             for feedback in self.feedback_service.get_all() if feedback.done is None])
        if message:
            update.message.reply_text(message)
        else:
            update.message.reply_text(self.texts['feedback-none'])

    @show_typing
    def _admin_feedback_reply(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        text = update.message.text[len("/admin-feedback-reply"):].strip()
        parts = text.split(" ")
        if len(parts) < 2:
            update.message.reply_text(self.texts['feedback-include-id'])
            return
        feedback_id = parts[0]
        text = text[len(feedback_id):].strip()

        feedback = self.feedback_service.get(int(feedback_id))
        if not feedback:
            update.message.reply_text(self.texts['feedback-not-found'])
            return
        bot.send_message(feedback.user_id, f"{self.texts['feedback-reply-prefix']}\n{text}\n\n"
                                           f"{self.texts['feedback-reply-postfix']}")
        update.message.reply_text(self.texts['feedback-reply-sent'])

    @show_typing
    def _admin_feedback_close(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        feedback_id = update.message.text[len("/admin-feedback-close"):].strip()
        if len(feedback_id) < 1:
            update.message.reply_text(self.texts['feedback-include-id'])
            return
        self.feedback_service.set_resolved(int(feedback_id))
        update.message.reply_text(self.texts['feedback-closed'])

    @show_typing
    def _admin_announce(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        text = update.message.text[len("/admin-announce"):].strip()
        if len(text) < 1:
            update.message.reply_text(self.texts['missing-text'](self.texts['admin']))
            return
        users = self.user_service.get_all_users()
        message = f"{self.texts['announcement-prefix']}\n{text}\n\n{self.texts['feedback-reply-postfix']}"
        for user_id in users:
            bot.send_message(user_id, message)
        update.message.reply_text(self.texts['announcement-sent'](len(users)))

    def _chat_member_add(self, bot, update):
        chat_id = update.message.chat.id
        for member in update.message.new_chat_members:
            if not member.is_bot:
                self._register_user(chat_id, member, update)
            if member.username == self.bot_name:
                update.message.reply_text(self.texts['welcome-bot'])
        if len(update.message.new_chat_members) < 1:
            if update.effective_chat.type == "private":
                if len(self.telegram_service.get_chats(bot, update.effective_user.id)) < 1:
                    update.message.reply_text(self.texts['add-to-group'])
                else:
                    update.message.reply_text(self.texts['help'])
            else:
                self._register_user(chat_id, update.effective_user, update)

    def _chat_member_remove(self, bot, update):
        chat_id = update.message.chat_id
        user_id = update.message.left_chat_member.id
        if self.user_service.remove_user_chat_if_exists(user_id, chat_id):
            # TODO: show deleted tasks?
            self.task_service.remove_tasks(user_id, chat_id)
            update.message.reply_text(self.texts['user-goodbye'](update.message.left_chat_member.first_name))

    def _inline_handler(self, bot, update, user_data):
        data = update.callback_query.data.split(":")
        if data[0] == "complete":
            task = self.task_service.get_task(data[1])
            if self.task_service.complete_task(data[1]):
                self.telegram_service.remove_inline_keybaord(bot, update.callback_query)
                owner_name = self.telegram_service.get_mention(bot, task.chat_id, task.owner_id)
                user_name = self.telegram_service.get_mention(bot, task.chat_id, task.user_id)
                update.callback_query.message.reply_text(self.texts['task-done'](task.title), quote=False)
                bot.send_message(
                    task.chat_id, self.texts['task-done-to-group'](owner_name, user_name, task.title),
                    parse_mode=telegram.ParseMode.MARKDOWN)
        elif len(data) > 1:
            self.telegram_service.remove_inline_keybaord(bot, update.callback_query)
            user_data[data[0]] = int(data[1])
            if "user_id" not in user_data:
                self._do_select_user(bot, update.callback_query.message, user_data)
            elif "due" not in user_data:
                self._do_select_due(bot, update.callback_query.message, user_data)
            else:
                user_data.clear()
                raise RuntimeError("Invalid state, clearing input.")
        else:
            selected, date = telegramcalendar.process_calendar_selection(bot, update)
            if selected:
                user_data['due'] = date
                self._do_add_task(bot, update.callback_query.message, user_data)
                user_data.clear()

        update.callback_query.answer()

    def _job_daily_tasks_show_all(self, bot, update):
        self._show_task_overviews(bot, True)

    def _job_daily_tasks_show_daily(self, bot, update):
        self._show_task_overviews(bot, False)

    def _job_weekly_review(self, bot, update):
        self._show_weekly_review(bot)

    def _error_handler(self, bot, update, error):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, error)

    def _register_user(self, chat_id, member, update):
        if self.user_service.add_user_chat_if_not_exists(member.id, chat_id):
            update.message.reply_text(self.texts['user-welcome'](update.message.chat.title, member.first_name) +
                                      "\n\n" + self.texts['help'])

    def _assure_private_chat(self, update):
        if not self.telegram_service.is_private_chat(update):
            update.message.reply_text(self.texts['private-chat-required'])
            return False
        return True

    def _get_task_markup(self, task):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=self.texts['btn-complete'](task.title), callback_data=f"complete:{task.id}")]],
            one_time_keyboard=True)

    def _show_task_overviews(self, bot, show_future_tasks):
        for user_id in self.user_service.get_all_users():
            tasks_summary = self._get_task_summary(bot, user_id, show_future_tasks)
            if len(tasks_summary) > 0:
                bot.send_message(user_id, tasks_summary)

    def _get_task_summary(self, bot, user_id, show_future_tasks):
        due_past = self.task_service.get_due_past(user_id)
        due_today = self.task_service.get_due_today(user_id)
        due_this_week = self.task_service.get_due_this_week(user_id)
        due_later_than_this_week = self.task_service.get_due_later_than_this_week(user_id)
        due_undefined = self.task_service.get_due_undefined(user_id)
        summary = (f"{self.texts['summary-overdue']}:\n{self._to_task_list(bot, due_past)}\n\n" if due_past else "") + \
                  (f"{self.texts['summary-due-today']}:\n{self._to_task_list(bot, due_today)}\n\n" if due_today else "")
        if show_future_tasks:
            summary += (f"{self.texts['summary-due-this-week']}:\n" +
                        f"{self._to_task_list(bot, due_this_week)}\n\n" if due_this_week else "") + \
                       (f"{self.texts['summary-due-later']}:\n"
                        f"{self._to_task_list(bot, due_later_than_this_week)}\n\n"
                        if due_later_than_this_week else "") + \
                       (f"{self.texts['summary-due-undefined']}:\n"
                        f"{self._to_task_list(bot, due_undefined)}\n\n" if due_undefined else "")
        return summary

    def _show_weekly_review(self, bot):
        for chat_id in self.user_service.get_all_chats():
            tasks = [task for task in self.task_service.get_tasks_for_chat(chat_id)
                     if task.done and task.done.date() > datetime.today().date() - timedelta(days=7)]
            if len(tasks) > 0:
                activity_counter = Counter([task.user_id for task in tasks])
                most_busy = activity_counter.most_common(1)[0][1]
                most_busy_users = [bot.getChatMember(chat_id, user_id).user.name
                                   for (user_id, count) in activity_counter.items() if count == most_busy]
                user_names = " and ".join(most_busy_users)
                message = f"{self.texts['task-review'](bot.getChat(chat_id).title)}:\n" \
                          f"{self._to_review_task_list(bot, tasks)}\n\n" \
                          f"{self.texts['task-review-most-busy'](user_names, len(most_busy_users) > 1)}\n\n" \
                          f"{self.texts['task-review-motivation']}"
                bot.send_message(chat_id, message)

    def _get_chat_tasks(self, bot, chat_id):
        tasks = [task for task in self.task_service.get_tasks_for_chat(chat_id) if not task.done]
        if len(tasks) < 1:
            return self.texts['no-tasks']

        return f"{self.texts['task-overview-group'](bot.getChat(chat_id).title)}:\n" \
               f"{self._to_group_task_list(bot, tasks)}\n\n" \
               f"{self.texts['task-overview-private-chat']}"

    def _to_group_task_list(self, bot, tasks):
        return "\n".join([self.texts['task-line-group'](task, bot.getChatMember(task.chat_id, task.user_id).user.name,
                                                        bot.getChatMember(task.chat_id, task.owner_id).user.name)
                          for task in tasks])

    def _to_task_list(self, bot, due_tasks):
        return "\n".join([self.texts['task-line'](bot.getChat(task.chat_id).title, task.title,
                                                  bot.getChatMember(task.chat_id, task.owner_id).user.name)
                          for task in due_tasks])

    def _to_review_task_list(self, bot, tasks):
        return "\n".join([self.texts['task-line-review'](task.title,
                                                         bot.getChatMember(task.chat_id, task.user_id).user.name,
                                                         bot.getChatMember(task.chat_id, task.owner_id).user.name) +
                          " " + self.texts['task-line-review-in-time'](task.done.date() <= task.due.date()
                                                                       if task.due else True)
                          for task in tasks if task.done])

    def _is_admin(self, user_id):
        return self.admin_id and self.admin_id == user_id

    def _get_stats_message(self, stats):
        return self.texts['tasks-stats-done'](
            stats['done']['count'], stats['done']['onTime'], stats['done']['late']) + \
               "\n" + self.texts['tasks-stats-open'](
            stats['open']['count'], stats['open']['onTime'], stats['open']['late'])
