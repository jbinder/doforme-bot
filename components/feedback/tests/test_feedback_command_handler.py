import os
import time
from unittest import mock

from telegram.ext import CommandHandler

from common.services.telegram_service import TelegramService
from common.test.PtbTestCase import PtbTestCase
from components.feedback.texts import texts
from components.feedback.feedback_command_handler import FeedbackCommandHandler
from components.user.user_service import UserService


class TestFeedbackCommandHandler(PtbTestCase):

    admin_id: int

    @mock.patch.dict(os.environ, {'DFM_ENV': 'Test'})
    def setUp(self):
        PtbTestCase.setUp(self)
        from components.feedback.models import db
        from components.feedback.feedback_service import FeedbackService
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.db = db
        self.admin_id = 42
        self.service = FeedbackService()
        self.handler = FeedbackCommandHandler(self.admin_id, texts, TelegramService(UserService()), self.service)

    def test_admin_feedback_show_no_feedback_is_no_admin(self):
        self.updater.dispatcher.add_handler(CommandHandler("show", self.handler.admin_feedback_show))
        self.updater.start_polling()
        update = self.mg.get_message(text="/show")

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # no message
        self.updater.stop()

    def test_admin_feedback_show_no_feedback_is_admin(self):
        self.updater.dispatcher.add_handler(CommandHandler("show", self.handler.admin_feedback_show))
        self.updater.start_polling()
        update = self.mg.get_message(text="/show")
        update.effective_user.id = self.admin_id

        self.bot.insertUpdate(update)

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # a warning message
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['feedback-none'], sent['text'])
        self.updater.stop()

    def test_feedback_add_no_text(self):
        self.updater.dispatcher.add_handler(CommandHandler("feedback", self.handler.feedback_add))
        self.updater.start_polling()
        update = self.mg.get_message(text="/feedback")

        self.bot.insertUpdate(update)

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # a warning message
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['missing-text'](update.effective_user.first_name), sent['text'])
        self.updater.stop()

    def test_feedback_add_includes_text(self):
        self.updater.dispatcher.add_handler(CommandHandler("feedback", self.handler.feedback_add))
        self.updater.start_polling()
        text = "some happy feedback"
        update = self.mg.get_message(text=f"/feedback {text}")

        self.bot.insertUpdate(update)

        self.assertEqual(3, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # a confirmation for the user
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['feedback-thanks'], sent['text'])
        sent = self.bot.sent_messages[2]
        # a notification for the admin
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['feedback-new'], sent['text'])
        self.assertEqual(self.admin_id, sent['chat_id'])
        self.updater.stop()

    def test_admin_feedback_show_has_feedback_is_admin(self):
        self.updater.dispatcher.add_handler(CommandHandler("show", self.handler.admin_feedback_show))
        self.updater.start_polling()
        update = self.mg.get_message(text="/show")
        update.effective_user.id = self.admin_id
        self.service.add(update.effective_user.id, "A very happy feedback...")

        self.bot.insertUpdate(update)
        time.sleep(1)  # the message takes some time to be sent...

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # a warning message
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertNotEqual(texts['feedback-none'], sent['text'])
        self.assertTrue(len(sent['text']) > 0)
        self.updater.stop()

    def test_admin_feedback_close_is_admin_valid_id(self):
        self.updater.dispatcher.add_handler(
            CommandHandler("admin-feedback-close", self.handler.admin_feedback_close))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-feedback-close 1")
        update.effective_user.id = self.admin_id
        self.service.add(update.effective_user.id, "A very happy feedback...")

        self.bot.insertUpdate(update)
        time.sleep(1)  # the message takes some time to be sent...

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # a confirmation message
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['feedback-closed'], sent["text"])
        self.updater.stop()

    def test_admin_feedback_reply_is_no_admin(self):
        self.updater.dispatcher.add_handler(CommandHandler("admin-feedback-reply", self.handler.admin_feedback_reply))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-feedback-reply")

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # no message
        self.updater.stop()

    def test_admin_feedback_reply_is_admin_no_arguments(self):
        self.updater.dispatcher.add_handler(CommandHandler("admin-feedback-reply", self.handler.admin_feedback_reply))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-feedback-reply")
        update.effective_user.id = self.admin_id

        self.bot.insertUpdate(update)

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # a warning message
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts["feedback-include-id"], sent['text'])
        self.updater.stop()

    def test_admin_feedback_reply_is_admin_invalid_id(self):
        self.updater.dispatcher.add_handler(CommandHandler("admin-feedback-reply", self.handler.admin_feedback_reply))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-feedback-reply 1 some nice reply")
        update.effective_user.id = self.admin_id

        self.bot.insertUpdate(update)
        time.sleep(1)  # the message takes some time to be sent...

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        sent = self.bot.sent_messages[1]
        # a warning message
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts["feedback-not-found"], sent['text'])
        self.updater.stop()

    def test_admin_feedback_reply_is_admin_valid_id(self):
        self.updater.dispatcher.add_handler(CommandHandler("admin-feedback-reply", self.handler.admin_feedback_reply))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-feedback-reply 1 some nice reply")
        update.effective_user.id = self.admin_id  # set the user id for the admin check
        update.message.chat.id = self.admin_id  # set the user id for the reply
        self.service.add(update.effective_user.id, "A very happy feedback...")

        self.bot.insertUpdate(update)
        time.sleep(1)  # the message takes some time to be sent...

        self.assertEqual(3, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # a reply message for the user
        sent = self.bot.sent_messages[1]
        self.assertEqual("sendMessage", sent['method'])
        self.assertTrue(len(sent['text']) > 0)
        self.assertNotEqual(texts["feedback-not-found"], sent['text'])
        # a confirmation message for the admin
        sent = self.bot.sent_messages[2]
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts["feedback-reply-sent"], sent['text'])
        self.assertEqual(self.admin_id, sent['chat_id'])
        self.updater.stop()

    def test_admin_feedback_close_is_no_admin(self):
        self.updater.dispatcher.add_handler(CommandHandler("admin-feedback-close", self.handler.admin_feedback_close))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-feedback-close")

        self.bot.insertUpdate(update)

        self.assertEqual(1, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        # no message
        self.updater.stop()

    def test_admin_feedback_close_is_admin_no_id(self):
        self.updater.dispatcher.add_handler(
            CommandHandler("admin-feedback-close", self.handler.admin_feedback_close))
        self.updater.start_polling()
        update = self.mg.get_message(text="/admin-feedback-close")
        update.effective_user.id = self.admin_id

        self.bot.insertUpdate(update)

        self.assertEqual(2, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        self.assertEqual("sendChatAction", sent['method'])
        self.assertEqual("typing", sent['action'])
        sent = self.bot.sent_messages[1]
        # a warning message
        self.assertEqual("sendMessage", sent['method'])
        self.assertEqual(texts['feedback-include-id'], sent["text"])
        self.updater.stop()
