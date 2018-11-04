from telegram.ext import CommandHandler

from common.services.telegram_service import TelegramService
from common.test.PtbTestCase import PtbTestCase
from components.core.core_command_handler import CoreCommandHandler
from components.user.user_service import UserService


class TestCoreCommandHandler(PtbTestCase):

    def setUp(self):
        PtbTestCase.setUp(self)
        self.handler = CoreCommandHandler(0, {'help': 'test'}, TelegramService(UserService()))

    def test_help(self):
        self.updater.dispatcher.add_handler(CommandHandler("help", self.handler.help_show))
        self.updater.start_polling()
        update = self.mg.get_message(text="/help")

        self.bot.insertUpdate(update)

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual("test", sent['text'])
        self.updater.stop()
