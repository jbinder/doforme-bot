import time

from telegram.ext import CommandHandler

from common.services.telegram_service import TelegramService
from common.test.PtbTestCase import PtbTestCase
from components.announce.announce_command_handler import AnnounceCommandHandler
from components.user.user_service import UserService
from components.announce.texts import texts


class TestAnnounceCommandHandler(PtbTestCase):

    def setUp(self):
        PtbTestCase.setUp(self)
        from components.user.models import db
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.service = UserService()
        self.admin_id = 42
        self.handler = AnnounceCommandHandler(self.admin_id, texts, TelegramService(self.service), self.service)

    def test_admin_announce_no_text(self):
        self.updater.dispatcher.add_handler(CommandHandler("admin-announce", self.handler.admin_announce))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-announce")
        update.effective_user.id = self.admin_id

        self.bot.insertUpdate(update)

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['missing-text'](texts['admin']), sent['text'])
        self.updater.stop()

    def test_admin_announce_valid_text_users_exist(self):
        self.updater.dispatcher.add_handler(CommandHandler("admin-announce", self.handler.admin_announce))
        self.updater.start_polling()
        text = "a very special announcement"
        update = self.mg.get_message(text=f"/admin-announce {text}")
        update.effective_user.id = self.admin_id
        self.service.add_user_chat_if_not_exists(update.effective_user.id, update.effective_chat.id)

        self.bot.insertUpdate(update)
        time.sleep(1)  # the message takes some time to be sent...

        self.assertEqual(3, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # the announcement sent to the user
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertTrue(text in sent['text'])
        # the confirmation for the admin
        sent = self.bot.sent_messages[2]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['announcement-sent'](1), sent['text'])
        update.effective_user.id = self.admin_id  # set the user id for the admin check
        update.message.chat.id = self.admin_id  # set the user id for the reply
        self.updater.stop()
