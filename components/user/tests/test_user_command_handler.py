import os
import time
from unittest import mock

from telegram.ext import MessageHandler, Filters

from common.services.telegram_service import TelegramService
from common.test.PtbTestCase import PtbTestCase
from components.user.texts import texts
from components.user.user_command_handler import UserCommandHandler


class TestUserCommandHandler(PtbTestCase):

    admin_id: int
    bot_name: str

    @mock.patch.dict(os.environ, {'DFM_ENV': 'Test'})
    def setUp(self):
        PtbTestCase.setUp(self)
        from components.user.models import db
        from components.user.user_service import UserService
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.db = db
        self.admin_id = 42
        self.service = UserService()
        self.bot_name = "botname"
        self.handler = UserCommandHandler(self.admin_id, texts, TelegramService(self.service), self.bot_name, self.service)

    def test_chat_member_add_no_new_chat_members_private_chat_no_chat_exists_for_user(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.new_chat_members, self.handler.chat_member_add))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.handler.chat_member_add))
        self.updater.start_polling()
        update = self.mg.get_message(text="hello!")

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        # info message
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['add-to-group'], sent['text'])
        self.updater.stop()

    def test_chat_member_add_no_new_chat_members_private_chat_exists_for_user(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.new_chat_members, self.handler.chat_member_add))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.handler.chat_member_add))
        self.updater.start_polling()
        update = self.mg.get_message(text="hello!")
        self.service.add_user_chat_if_not_exists(update.effective_user.id, update.effective_chat.id)

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        # help message
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['help'], sent['text'])
        self.updater.stop()

    def test_chat_member_add_no_new_chat_members_group_user_does_not_exist(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.new_chat_members, self.handler.chat_member_add))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.handler.chat_member_add))
        self.updater.start_polling()
        chat = self.cg.get_chat(type="group")
        update = self.mg.get_message(text="hello!", chat=chat)

        self.bot.insertUpdate(update)
        time.sleep(1)  # the message takes some time to be sent...

        self.assertEqual(1, len(self.bot.sent_messages))
        # welcome message
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendMessage", sent['method'])
        self.assertTrue(update.effective_user.first_name in sent['text'])
        self.updater.stop()

    def test_chat_member_add_new_chat_member(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.new_chat_members, self.handler.chat_member_add))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.handler.chat_member_add))
        self.updater.start_polling()
        user = self.ug.get_user()
        chat = self.cg.get_chat(type="group")
        update = self.mg.get_message(text="hello!", chat=chat)
        update.message.new_chat_members = [user]

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        # welcome message
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendMessage", sent['method'])
        self.assertTrue(user.first_name in sent['text'])
        self.updater.stop()

    def test_chat_member_add_new_chat_member_bot(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.new_chat_members, self.handler.chat_member_add))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.handler.chat_member_add))
        self.updater.start_polling()
        user = self.ug.get_user(is_bot=True, username=self.bot_name)
        chat = self.cg.get_chat(type="group")
        update = self.mg.get_message(text="hello!", chat=chat)
        update.message.new_chat_members = [user]

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        # welcome message
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['welcome-bot'], sent['text'])
        self.updater.stop()

    def test_chat_member_add_no_new_chat_members_group_user_exists(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.new_chat_members, self.handler.chat_member_add))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.handler.chat_member_add))
        self.updater.start_polling()
        chat = self.cg.get_chat(type="group")
        update = self.mg.get_message(text="hello!", chat=chat)
        self.service.add_user_chat_if_not_exists(update.effective_user.id, chat.id)

        self.bot.insertUpdate(update)

        self.assertEqual(0, len(self.bot.sent_messages))
        # welcome message
        self.updater.stop()

    def test_chat_member_remove_chat_member_does_not_exist(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.left_chat_member, self.handler.chat_member_remove))
        self.updater.start_polling()
        user = self.ug.get_user()
        chat = self.cg.get_chat(type="group")
        update = self.mg.get_message(left_chat_member=user, chat=chat)

        self.bot.insertUpdate(update)

        self.assertEqual(0, len(self.bot.sent_messages))
        # no message
        self.updater.stop()

    def test_chat_member_remove_chat_member_exists(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.status_update.left_chat_member, self.handler.chat_member_remove))
        self.updater.start_polling()
        user = self.ug.get_user()
        chat = self.cg.get_chat(type="group")
        update = self.mg.get_message(left_chat_member=user, chat=chat)
        self.service.add_user_chat_if_not_exists(user.id, chat.id)

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        # goodbye message
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['user-goodbye'](user.first_name), sent['text'])
        self.updater.stop()
