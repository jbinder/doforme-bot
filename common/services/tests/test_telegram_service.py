import types
from unittest.mock import MagicMock

from common.services.telegram_service import TelegramService
from common.test.PtbTestCase import PtbTestCase
from components.user.user_service import UserService


class TestFeedbackService(PtbTestCase):

    def setUp(self):
        PtbTestCase.setUp(self)

        self.user_service = UserService()

        self.service = TelegramService(self.user_service)

    def test_is_private_chat_is_private_chat(self):
        update = self.mg.get_message(text="/help")

        is_private_chat = self.service.is_private_chat(update)

        self.assertTrue(is_private_chat)

    def test_is_private_chat_is_group_chat(self):
        chat = self.cg.get_chat(type="group")
        update = self.mg.get_message(chat=chat)

        is_private_chat = self.service.is_private_chat(update)

        self.assertFalse(is_private_chat)

    def test_get_mention(self):
        user_result = types.SimpleNamespace()
        user_result.user = self.ug.get_user()
        self.bot.getChatMember = MagicMock(return_value=user_result)
        user_id = 3

        actual = self.service.get_mention(self.bot, 2, user_id)

        self.assertEqual(f"[{user_result.user.name}](tg://user?id={user_id})", actual)

    def test_get_chat_users(self):
        user_result = types.SimpleNamespace()
        user_result.user = self.ug.get_user()
        self.bot.getChatMember = MagicMock(return_value=user_result)
        chat_id = 2
        self.user_service.add_user_chat_if_not_exists(3, chat_id)

        actual = self.service.get_chat_users(self.bot, chat_id)

        self.assertGreater(len(actual), 0)

    def test_get_chats(self):
        self.bot.getChat = MagicMock(return_value=self.cg.get_chat())
        user_id = 2
        self.user_service.add_user_chat_if_not_exists(user_id, 3)

        actual = self.service.get_chats(self.bot, user_id)

        self.assertGreater(len(actual), 0)
