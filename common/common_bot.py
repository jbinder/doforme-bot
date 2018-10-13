from logging import Logger
from queue import Queue
from threading import Thread

from telegram import Bot
from telegram.ext import Updater, Dispatcher
from telegram.ext.jobqueue import JobQueue


class CommonBot:
    logger: Logger
    components: dict

    def __init__(self, components, logger):
        self.components = components
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

    def _error_handler(self, bot, update, error):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, error)
