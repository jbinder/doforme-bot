import abc
from typing import List

from telegram.ext import Dispatcher, CommandHandler


class ComponentBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def init(self, dp: Dispatcher):
        """ Handle initialization here, like registering commands. """

    @abc.abstractmethod
    def get_stats(self):
        """ Return a dictionary of component specific statistics. """

    @staticmethod
    def _register_commands(dp: Dispatcher, cmd_handlers: List):
        [dp.add_handler(CommandHandler(command, callback, pass_user_data=pass_user_data))
         for command, callback, pass_user_data in cmd_handlers]

