from __future__ import absolute_import

import unittest

from telegram.ext import CommandHandler
from telegram.ext import Updater

import ptbtest

from common.services.telegram_service import TelegramService
from components.core.core_command_handler import CoreCommandHandler
from components.user.user_service import UserService


class TestCoreCommandHandler(unittest.TestCase):
    def setUp(self):
        self.bot = ptbtest.Mockbot()
        self.ug = ptbtest.UserGenerator()
        self.cg = ptbtest.ChatGenerator()
        self.mg = ptbtest.MessageGenerator(self.bot)
        self.updater = Updater(bot=self.bot)
        self.handler = CoreCommandHandler(0, {'help': 'test'}, TelegramService(UserService()))

    def test_help(self):
        self.updater.dispatcher.add_handler(CommandHandler("help", self.handler.help_show))
        self.updater.start_polling()
        update = self.mg.get_message(text="/help")

        self.bot.insertUpdate(update)

        self.assertEqual(len(self.bot.sent_messages), 2)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendChatAction")
        self.assertEqual(sent['action'], "typing")
        sent = self.bot.sent_messages[1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], "test")
        self.updater.stop()
