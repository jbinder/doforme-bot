from queue import Queue
from threading import Thread

from telegram import Bot
from telegram.ext import Updater, CommandHandler, Dispatcher
from telegram.ext.jobqueue import JobQueue

from components.user.user_service import UserService
from common.decorators.show_typing import show_typing


class DoForMeBot:
    bot_name: str
    texts: dict
    user_service: UserService
    components: dict

    def __init__(self, bot_name, texts, components, admin_id, logger, user_service):
        self.bot_name = bot_name
        self.texts = texts
        self.components = components
        self.user_service = user_service
        self.admin_id = admin_id
        self.logger = logger

    def run(self, token, webhook_url=None):
        if webhook_url:
            bot = Bot(token)
            update_queue = Queue()
            job_queue = JobQueue(bot)
            dp = Dispatcher(bot, update_queue, job_queue=job_queue)
        else:
            updater = Updater(token)
            bot = updater.bot
            dp = updater.dispatcher

        cmd_handlers = [
            ('start', self._help_show, False),
            ('help', self._help_show, False),
            ('admin-announce', self._admin_announce, False),
        ]
        [dp.add_handler(CommandHandler(command, callback, pass_user_data=pass_user_data))
         for command, callback, pass_user_data in cmd_handlers]

        for component in self.components.values():
            component.init(dp)

        dp.add_error_handler(self._error_handler)

        if webhook_url:
            bot.set_webhook(webhook_url=webhook_url)
            job_queue.start()
            thread = Thread(target=dp.start, name='dispatcher')
            thread.start()
            return update_queue, bot
        else:
            bot.set_webhook()
            updater.start_polling()
            updater.idle()

    @show_typing
    def _help_show(self, bot, update):
        update.message.reply_text(self.texts['help'])

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

    def _error_handler(self, bot, update, error):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, error)

    def _is_admin(self, user_id):
        return self.admin_id and self.admin_id == user_id
