import abc
from typing import List

from telegram.ext import Dispatcher, CommandHandler, MessageHandler

from common.event_type import EventType


class ComponentBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def init(self, dp: Dispatcher):
        """ Handle initialization here, like registering commands. """

    @abc.abstractmethod
    def get_stats(self):
        """ Return a dictionary of component specific statistics. """

    @abc.abstractmethod
    def register_observer(self, event_type: EventType, observer: callable):
        """ Register for observing component events. """

    @staticmethod
    def _register_command_handlers(dp: Dispatcher, command_handlers: List):
        [dp.add_handler(CommandHandler(command, callback, pass_user_data=pass_user_data))
         for command, callback, pass_user_data in command_handlers]

    @staticmethod
    def _register_message_handlers(dp: Dispatcher, message_handlers: List):
        [dp.add_handler(MessageHandler(filters, callback)) for (filters, callback) in message_handlers]
