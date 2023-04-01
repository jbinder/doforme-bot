import operator
import re
from collections import Counter
from datetime import datetime, timedelta, date

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from common.command_handler_base import CommandHandlerBase
from components.core.job_log_service import JobLogService
from components.doforme.task_service import TaskService
from components.feedback.feedback_service import FeedbackService
from components.user.user_event_type import UserEventType
from components.user.user_service import UserService
from common.decorators.show_typing import show_typing
from libraries.calendar import telegramcalendar
from dateutil.relativedelta import relativedelta


class DoForMeCommandHandler(CommandHandlerBase):
    _date_format: str
    user_service: UserService
    feedback_service: FeedbackService
    bot_name: str
    task_service: TaskService
    show_all_tasks_weekday: int
    job_log_service: JobLogService

    def __init__(self, admin_id, texts, telegram_service, bot_name, task_service, user_service, feedback_service,
                 show_all_tasks_weekday, job_log_service):
        super().__init__(admin_id, texts, telegram_service)
        self.feedback_service = feedback_service
        self.user_service = user_service
        self.bot_name = bot_name
        self.task_service = task_service
        self.show_all_tasks_weekday = show_all_tasks_weekday
        self.job_log_service = job_log_service
        self._date_format = "%Y-%m-%d"
        self.register_observer(
            UserEventType.USER_LEFT_CHAT,
            lambda event: task_service.remove_tasks(event['user_id'], event['chat_id']))

    @show_typing
    def do_select_chat(self, bot, update, user_data):
        user_data.clear()

        text = update.message.text[len("/do"):].strip()

        _line_title = text.split("\n")[0]
        _line_description = "\n".join(text.split("\n")[1:])

        # escape title to avoid issues when sending it as markdown in e.g. reply_text
        user_data['description'] = DoForMeCommandHandler._escape_text(_line_description)
        user_data['owner_id'] = update.effective_user.id

        if not self.telegram_service.is_private_chat(update):
            self._add_task_inline(bot, update, text, user_data)
            return

        user_data['title'] = DoForMeCommandHandler._escape_text(_line_title)
        if text == f"@{self.bot_name}" or not text:
            self.telegram_service.send_reply(update.message, self.texts['missing-title'](update.effective_user.first_name))
            return
        chats = self.telegram_service.get_chats(bot, update.effective_user.id)
        if len(chats) < 1:
            self.telegram_service.send_reply(update.message, self.texts['add-to-group'])
            return

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=chat_name, callback_data=f"chat_id:{chat_id}")]
             for (chat_id, chat_name) in chats])
        self.telegram_service.send_reply(update.message, self.texts['select-chat'], reply_markup=markup, quote=False)

    def _add_task_inline(self, bot, update, text, user_data):
        def parse_command(command):
            match = re.match("([^@]*)@?(.*)\s+in\s+(\d+)\s+(.*)", command)
            if match is None:
                return None
            groups = match.groups()
            if len(groups) != 4:
                return None
            return groups

        user_data['chat_id'] = update.message.chat_id

        mention = next((x for x in update.message.entities if x.type == 'text_mention'), None)

        if mention is None:
            # resolve user id by name
            chat_users = self.telegram_service.get_chat_users(bot, user_data['chat_id'])
            user_name_parsed = None
            parsed_text = parse_command(text)
            if parsed_text is not None:
                user_name_parsed = parsed_text[1].strip()
                user_data['user_id'] = next(
                    (user_id for (user_id, user_name) in chat_users if user_name == user_name_parsed), 0)
            if not parsed_text:
                self.telegram_service.send_reply(update.message, self.texts['help-do-group-format'])
                return
            if user_name_parsed and user_data['user_id'] == 0:
                self.telegram_service.send_reply(update.message, self.texts['help-do-group-user-not-registered'](user_name_parsed))
                return
        else:
            # resolve user id using message metadata
            text = update.message.text[:mention.offset] + '@' + update.message.text[mention.offset:]
            text = text[len("/do"):].strip()
            parsed_text = parse_command(text)
            if not parsed_text:
                self.telegram_service.send_reply(update.message, self.texts['help-do-group-format'])
                return
            user_data['user_id'] = mention.user.id

        user_data['title'] = DoForMeCommandHandler._escape_text(parsed_text[0].strip())

        unit = parsed_text[3] + 's' if parsed_text[3][-1:] != 's' else parsed_text[3]
        timedelta_args = {unit: int(parsed_text[2])}
        try:
            user_data['due'] = datetime.now() + relativedelta(**timedelta_args)
        except TypeError:
            self.telegram_service.send_reply(update.message, self.texts['help-do-group-format'])
            return

        self._do_add_task(bot, update.message, user_data, True)
        return

    # see https://stackoverflow.com/questions/40626896/telegram-does-not-escape-some-markdown-characters/49924429
    @staticmethod
    def _escape_text(text):
        return text\
            .replace("_", "\\_")\
            .replace("*", "\\*")\
            .replace("[", "\\[")\
            .replace("`", "\\`")

    def _do_select_user(self, bot, message, user_data):
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=user_name, callback_data=f"user_id:{user_id}")]
             for (user_id, user_name) in self.telegram_service.get_chat_users(bot, user_data['chat_id'])],
            one_time_keyboard=True)
        self.telegram_service.send_reply(message, self.texts['select-user'](user_data['title'], message.chat.first_name),
                           reply_markup=markup, quote=False, parse_mode=telegram.ParseMode.MARKDOWN)

    def _do_select_due(self, bot, message, user_data):
        reply = telegramcalendar.create_calendar(indicate_today=True)
        self.telegram_service.send_reply(message, self.texts['select-date'], reply_markup=reply)

    def _do_add_task(self, bot, message, user_data, in_group=False):
        user_id = user_data['user_id']
        chat_id = user_data['chat_id']
        user_data['is_group_task'] = user_id == 0
        user_name = self.telegram_service.get_mention(bot, chat_id, user_id)
        self.task_service.add_task(user_data)
        title_escaped = self.telegram_service.escape_text(user_data['title'])
        if not in_group:
            self.telegram_service.send_reply(message, self.texts['added-task'](user_name, title_escaped),
                                             quote=False, parse_mode=telegram.ParseMode.MARKDOWN,
                                             reply_markup=ReplyKeyboardRemove(), skip_escaping=True)
        owner_user_name = self.telegram_service.get_mention(bot, message.chat.id, user_data['owner_id'])
        self.telegram_service.send_message(bot, chat_id, self.texts['added-task-to-group'](owner_user_name, user_name,
                                                                                           title_escaped,
                                                                                           user_data['due']),
                                           parse_mode=telegram.ParseMode.MARKDOWN, skip_escaping=True)

    @show_typing
    def tasks_show(self, bot, update):
        if not self.telegram_service.is_private_chat(update):
            tasks = self._get_chat_tasks(bot, update.effective_chat.id)
            self.telegram_service.send_reply(update.message, tasks,
                                      parse_mode=telegram.ParseMode.MARKDOWN)
            group_tasks = [task for task in self.task_service.get_tasks(0) if not task.done]
            if len(group_tasks) > 0:
                self.telegram_service.send_reply(update.message, f"{self.texts['task-headline-assigned-group']}:",
                                                 parse_mode=telegram.ParseMode.MARKDOWN)
            for task in group_tasks:
                self._show_own_task(bot, task, update)
            return

        user_id = update.effective_user.id

        tasks = [task for task in self.task_service.get_tasks(user_id) if not task.done]
        self.telegram_service.send_reply(update.message, f"{self.texts['task-headline-assigned']}:")
        if len(tasks) < 1:
            self.telegram_service.send_reply(update.message, self.texts['no-tasks'])

        for task in tasks:
            self._show_own_task(bot, task, update)

        tasks = [task for task in self.task_service.get_owning_tasks(user_id) if not task.done]
        self.telegram_service.send_reply(update.message, f"{self.texts['task-headline-owning']}:\n")
        if len(tasks) < 1:
            self.telegram_service.send_reply(update.message, self.texts['no-tasks'])
        for task in tasks:
            task_summary = self.texts['task-line-summary'](task, bot.getChat(task.chat_id).title,
                                                           self.telegram_service.get_user_name(bot, task.chat_id, task.user_id))
            markup = self._get_owned_task_markup(task)
            self.telegram_service.send_reply(update.message, task_summary, reply_markup=markup, parse_mode=telegram.ParseMode.MARKDOWN)

    def _show_own_task(self, bot, task, update):
        if task.is_group_task:
            task_summary = self.texts['task-line-summary-group'](task,
                                                                 self.telegram_service.get_user_name(bot, task.chat_id,
                                                                                                     task.owner_id))
        else:
            task_summary = self.texts['task-line-summary'](task, bot.getChat(task.chat_id).title,
                                                           self.telegram_service.get_user_name(bot, task.chat_id,
                                                                                               task.owner_id))
        markup = self._get_assigned_task_markup(task)
        self.telegram_service.send_reply(update.message, task_summary, reply_markup=markup,
                                         parse_mode=telegram.ParseMode.MARKDOWN)

    @show_typing
    def stats_show(self, bot, update):
        if self.telegram_service.is_private_chat(update):
            stats = self.task_service.get_user_stats(update.effective_user.id)
            owning_message = self._get_stats_message(stats['owning'])
            assigned_message = self._get_stats_message(stats['assigned'])
            message = self.texts['task-stats'](stats['owning']['count'], owning_message,
                                               stats['assigned']['count'], assigned_message)
        else:
            stats = self.task_service.get_chat_stats(update.effective_chat.id)
            message = self._get_stats_message(stats)
        self.telegram_service.send_reply(update.message, message)

    @show_typing
    def admin_stats(self, bot, update):
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
        self.telegram_service.send_reply(update.message, message)

    def inline_handler(self, bot, update, user_data):
        data = re.split("[:,\n]", update.callback_query.data)
        if data[0] == "complete":
            user_id = update.effective_user.id
            task = self.task_service.get_task(data[1])
            if self.task_service.complete_task(data[1], user_id):
                self.telegram_service.remove_inline_keybaord(bot, update.callback_query)

                owner_name = self.telegram_service.get_mention(bot, task.chat_id, task.owner_id)\
                    if not task.is_group_task else "Everyone"
                user_name = self.telegram_service.get_mention(bot, task.chat_id,
                                                              task.user_id if not task.is_group_task else user_id)

                title_escaped = self.telegram_service.escape_text(task.title)
                if not task.is_group_task:
                    self.telegram_service.send_reply(update.callback_query.message, self.texts['task-done'](title_escaped),
                                                     quote=False, parse_mode=telegram.ParseMode.MARKDOWN, skip_escaping=True)
                self.telegram_service.send_message(bot,
                    task.chat_id, self.texts['task-done-to-group'](owner_name, user_name, title_escaped),
                    parse_mode=telegram.ParseMode.MARKDOWN, skip_escaping=True)
        elif data[0] == "edit-date":
            user_data['task_id'] = data[1]
            self._do_select_due(bot, update.callback_query.message, user_data)
        elif data[0] == "show-task":
            task = self.task_service.get_task(data[1])
            self.telegram_service.send_message(bot,
                task.owner_id, task.description,
                parse_mode=telegram.ParseMode.MARKDOWN)

        elif data[0] == "edit-due-deny":
            self._edit_due_deny(bot, data, update)
            self.telegram_service.remove_inline_keybaord(bot, update.callback_query)
        elif data[0] == "edit-due-accept":
            self._edit_due_accept(bot, data, update)
            self.telegram_service.remove_inline_keybaord(bot, update.callback_query)
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
                if 'task_id' in user_data:
                    self._edit_due_request(bot, date, update, user_data)
                else:
                    self._do_add_task(bot, update.callback_query.message, user_data)
                user_data.clear()

        update.callback_query.answer()

    def _edit_due_request(self, bot, date, update, user_data):
        task = self.task_service.get_task(user_data['task_id'])
        user_id = update.effective_user.id
        date_str = date.strftime(self._date_format)

        if task.is_group_task:
            # immediately update for group tasks
            new_due = datetime.strptime(date_str, self._date_format)
            self.task_service.update_due_date(task.id, new_due)
            self.telegram_service.send_reply(update.callback_query.message, self.texts['due-updated'])
            return

        data = f":{task.id}\nuser_id:{user_id}\ndate:{date_str}"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=self.texts['btn-accept'],
                                   callback_data=f"edit-due-accept" + data),
              InlineKeyboardButton(text=self.texts['btn-deny'],
                                   callback_data=f"edit-due-deny" + data)]],
            one_time_keyboard=True)
        requestee_id = task.user_id if user_id == task.owner_id else task.owner_id
        requestee_name = self.telegram_service.get_mention(bot, task.chat_id, requestee_id)
        requestor_name = self.telegram_service.get_mention(bot, task.chat_id, user_id)
        self.telegram_service.send_message(bot,
            requestee_id,
            self.texts['update-task-due-request'](requestor_name, self.telegram_service.escape_text(task.title), task.due, date),
            parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup, skip_escaping=True)
        self.telegram_service.send_reply(update.callback_query.message, self.texts['updated-task-requested'](requestee_name),
                                                 quote=False, parse_mode=telegram.ParseMode.MARKDOWN, skip_escaping=True)

    def _edit_due_deny(self, bot, data, update):
        new_due, requestee_name, requestor_name, task = self._get_edit_due_request_data(bot, data, update)
        self.telegram_service.send_message(bot, task.chat_id,
                         self.texts['update-task-due-denied'](
                             requestee_name, requestor_name, self.telegram_service.escape_text(task.title), task.due, new_due),
                         parse_mode=telegram.ParseMode.MARKDOWN, skip_escaping=True)
        self.telegram_service.send_reply(update.callback_query.message, self.texts['update-denied'])

    def _edit_due_accept(self, bot, data, update):
        new_due, requestee_name, requestor_name, task = self._get_edit_due_request_data(bot, data, update)
        prev_due = task.due
        self.task_service.update_due_date(task.id, new_due)
        chat_id = task.chat_id
        self.telegram_service.send_message(bot,
            chat_id, self.texts['update-task-due-accepted'](
                requestee_name, requestor_name, self.telegram_service.escape_text(task.title), prev_due, new_due),
            parse_mode=telegram.ParseMode.MARKDOWN, skip_escaping=True)
        self.telegram_service.send_reply(update.callback_query.message, self.texts['update-granted'])

    def _get_edit_due_request_data(self, bot, data, update):
        task = self.task_service.get_task(data[1])
        requestee_id = update.effective_user.id
        requestee_name = self.telegram_service.get_mention(bot, task.chat_id, requestee_id)
        requestor_id = data[3]
        requestor_name = self.telegram_service.get_mention(bot, task.chat_id, requestor_id)
        new_due = datetime.strptime(data[5], self._date_format)
        return new_due, requestee_name, requestor_name, task

    def _get_chat_tasks(self, bot, chat_id):
        tasks = [task for task in self.task_service.get_tasks_for_chat(chat_id) if not task.done]
        if len(tasks) < 1:
            return self.texts['no-tasks']

        return f"{self.texts['task-overview-group'](bot.getChat(chat_id).title)}:\n" \
            f"{self._to_group_task_list(bot, tasks)}\n\n" \
            f"{self.texts['task-overview-private-chat']}"

    def _get_assigned_task_markup(self, task):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=self.texts['btn-complete'], callback_data=f"complete:{task.id}"),
              InlineKeyboardButton(text=self.texts['btn-edit-date'], callback_data=f"edit-date:{task.id}"),
              InlineKeyboardButton(text=self.texts['btn-show-task'], callback_data=f"show-task:{task.id}")]],
            one_time_keyboard=True)

    def _get_owned_task_markup(self, task):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=self.texts['btn-edit-date'], callback_data=f"edit-date:{task.id}")]],
            one_time_keyboard=True)

    def _get_stats_message(self, stats):
        return self.texts['tasks-stats-done'](
            stats['done']['count'], stats['done']['onTime'], stats['done']['late']) + \
               "\n" + self.texts['tasks-stats-open'](
            stats['open']['count'], stats['open']['onTime'], stats['open']['late'])

    def _show_task_overviews(self, bot, show_near_future_tasks, show_far_future_tasks=False):
        for user_id in self.user_service.get_all_users():
            tasks_summary = self._get_task_summary(bot, user_id, show_near_future_tasks, show_far_future_tasks)
            if len(tasks_summary) > 0:
                self.telegram_service.send_message(bot, user_id, tasks_summary, parse_mode=telegram.ParseMode.MARKDOWN)

        for chat_id in self.user_service.get_all_chats():
            tasks = [task for task in self.task_service.get_tasks_for_chat(chat_id)
                     if not task.done and task.is_group_task and task.due.date() == datetime.today().date()]
            if len(tasks) > 0:
                message = (f"{self.texts['summary-due-today']}:\n{self._to_group_task_list(bot, tasks)}\n\n"
                           if tasks else "")
                self.telegram_service.send_message(bot, chat_id, message, parse_mode=telegram.ParseMode.MARKDOWN)

    def _get_task_summary(self, bot, user_id, show_near_future_tasks, show_far_future_tasks):
        due_past = self.task_service.get_due_past(user_id)
        due_today = self.task_service.get_due_today(user_id)
        summary = (f"{self.texts['summary-overdue']}:\n{self._to_task_list(bot, due_past)}\n\n" if due_past else "") + \
                  (f"{self.texts['summary-due-today']}:\n{self._to_task_list(bot, due_today)}\n\n" if due_today else "")
        if show_near_future_tasks:
            due_this_week = self.task_service.get_due_this_week(user_id)
            summary += (f"{self.texts['summary-due-this-week']}:\n" +
                        f"{self._to_task_list(bot, due_this_week)}\n\n" if due_this_week else "")
        if show_far_future_tasks:
            due_later_than_this_week = self.task_service.get_due_later_than_this_week(user_id)
            summary += (f"{self.texts['summary-due-later']}:\n"
                        f"{self._to_task_list(bot, due_later_than_this_week)}\n\n"
                        if due_later_than_this_week else "")
        due_undefined = self.task_service.get_due_undefined(user_id)
        summary += (f"{self.texts['summary-due-undefined']}:\n"
                    f"{self._to_task_list(bot, due_undefined)}\n\n" if due_undefined else "")
        if len(summary) > 0:
            summary = f"{self.texts['summary-headline']}:\n\n" + summary
        return summary

    def _show_weekly_review(self, bot):
        for chat_id in self.user_service.get_all_chats():
            message = f"{self.texts['task-review'](bot.getChat(chat_id).title)}:\n\n"

            now = datetime.now()
            last_week = now - timedelta(days=7)
            week_before = last_week - timedelta(days=7)
            next_week = now + timedelta(days=7)
            stats = self.task_service.get_stats(chat_id, last_week, now)
            previous_stats = self.task_service.get_stats(chat_id, week_before, last_week)
            has_activity = stats[0]['count'] > 0 or stats[1]['count'] > 0
            if has_activity:
                on_time = stats[1]['done']['onTimePercent']
                created_change = stats[0]['count'] - previous_stats[0]['count']
                done_change = stats[1]['count'] - previous_stats[1]['count']
                on_time_change = previous_stats[1]['done']['onTimePercent'] / on_time if on_time > 0 else \
                    previous_stats[1]['done']['onTimePercent']
                message = message + \
                          f"{self.texts['task-review-summary'](stats[0]['count'], stats[1]['count'], on_time)} " \
                              f"{self.texts['task-review-comparison'](created_change, done_change, on_time_change)}\n\n"

                tasks = [task for task in self.task_service.get_tasks_for_chat(chat_id)
                         if task.done and task.done > last_week]
                if len(tasks) > 0:
                    activity_counter = Counter([task.user_id for task in tasks])
                    most_busy = activity_counter.most_common(1)[0][1]
                    most_busy_users = [self.telegram_service.get_user_name(bot, chat_id, user_id)
                                       for (user_id, count) in activity_counter.items() if count == most_busy]
                    user_names = " and ".join(most_busy_users)
                    message = message + self.texts['task-review-done-tasks'] + "\n" + \
                              f"{self._to_review_task_list(bot, tasks)}\n\n" \
                                  f"{self.texts['task-review-most-busy'](user_names, len(most_busy_users) > 1)}\n\n"
            else:
                message = message + self.texts['nothing'] + "\n\n"

            open_tasks = [task for task in self.task_service.get_tasks_for_chat(chat_id)
                          if (task.done is None and task.due.date() <= datetime.today().date())]
            has_open_tasks = len(open_tasks) > 0
            if has_open_tasks:
                open_tasks.sort(key=lambda x: x.due)
                message = message + self.texts['task-review-incomplete-tasks'] + "\n" + \
                          f"{self._to_review_due_task_list(bot, open_tasks)}\n\n"

            if has_activity and not has_open_tasks:
                message = message + self.texts['nothing'] + "\n\n"

            upcoming_tasks = [task for task in self.task_service.get_tasks_for_chat(chat_id)
                              if (task.done is None and datetime.today().date() <= task.due.date() <= next_week.date())]
            has_upcoming_tasks = len(upcoming_tasks) > 0
            if has_upcoming_tasks:
                upcoming_tasks.sort(key=lambda x: x.due)
                message = message + self.texts['task-review-upcoming-tasks'] + "\n" + \
                          f"{self._to_review_upcoming_task_list(bot, upcoming_tasks)}\n\n"

            if not has_activity and not has_open_tasks and not has_upcoming_tasks:
                return

            stats = []
            message = message + f"{self.texts['ranking']}:\n"
            for (user_id, user_name) in self.telegram_service.get_chat_users(bot, chat_id):
                user_stats = self.task_service.get_stats(chat_id, user_id=user_id)
                done = user_stats[1]['done']['count']
                on_time = user_stats[1]['done']['onTimePercent']
                stats.append([user_name, done, on_time])

            stats.sort(key=operator.itemgetter(1, 2), reverse=True)
            for user_name, done, on_time in stats:
                message = message + self.texts['task-review-user-stats'](user_name, done, on_time) + "\n"

            message = message + f"\n{self.texts['task-review-motivation']}"
            self.telegram_service.send_message(bot, chat_id, message, parse_mode=telegram.ParseMode.MARKDOWN)

    def _to_group_task_list(self, bot, tasks):
        return "\n".join([self.texts['task-line-group'](task, self.telegram_service.get_user_name(bot, task.chat_id, task.user_id),
                                                        self.telegram_service.get_user_name(bot, task.chat_id, task.owner_id))
                          for task in tasks if task.is_group_task])

    def _to_task_list(self, bot, due_tasks):
        return "\n".join([self.texts['task-line'](bot.getChat(task.chat_id).title, task.title,
                                                  self.telegram_service.get_user_name(bot, task.chat_id, task.owner_id))
                          for task in due_tasks])

    def _to_review_task_list(self, bot, tasks):
        return "\n".join([self.texts['task-line-review'](task.title,
                                                         self.telegram_service.get_user_name(bot, task.chat_id, task.user_id),
                                                         self.telegram_service.get_user_name(bot, task.chat_id, task.owner_id)) +
                          " " + self.texts['task-line-review-in-time'](task.done.date() <= task.due.date()
                                                                       if task.due else True)
                          for task in tasks if task.done])

    def _to_review_due_task_list(self, bot, tasks):
        return "\n".join([self.texts['task-line-review-incomplete']
                          (task.title,
                           self.telegram_service.get_user_name(bot, task.chat_id, task.user_id),
                           self.telegram_service.get_user_name(bot, task.chat_id, task.owner_id),
                           (datetime.now() - task.due).days)
                          for task in tasks])

    def _to_review_upcoming_task_list(self, bot, tasks):
        return "\n".join([self.texts['task-line-review-upcoming']
                          (task.title,
                           self.telegram_service.get_user_name(bot, task.chat_id, task.user_id),
                           self.telegram_service.get_user_name(bot, task.chat_id, task.owner_id),
                           (task.due - datetime.now()).days)
                          for task in tasks])

    def job_daily_tasks_show_all(self, bot, update):
        job_name = 'daily_tasks_show_all'
        is_admin = self._is_admin(update.effective_user.id)
        if self.job_log_service.has_run_recently(job_name) and not is_admin:
            return
        show_all = date.today().weekday() == self.show_all_tasks_weekday
        self._show_task_overviews(bot, True, show_all)
        self.job_log_service.update_job_log(job_name)

    def job_daily_tasks_show_daily(self, bot, update):
        job_name = 'daily_tasks_show_daily'
        if self.job_log_service.has_run_recently(job_name):
            return
        self._show_task_overviews(bot, False)
        self.job_log_service.update_job_log(job_name)

    def job_weekly_review(self, bot, update):
        job_name = 'weekly_review'
        if self.job_log_service.has_run_recently(job_name):
            return
        self._show_weekly_review(bot)
        self.task_service.clean_data()
        self.job_log_service.update_job_log(job_name)
