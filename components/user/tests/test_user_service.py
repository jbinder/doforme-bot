import os
import unittest
from unittest import mock

from pony.orm import Database


class TestUserService(unittest.TestCase):

    chat1_id: int
    user1_id: int
    db: Database

    @mock.patch.dict(os.environ, {'DFM_ENV': 'Test'})
    def setUp(self):
        from components.user.models import db
        from components.user.user_service import UserService
        self.service = UserService()
        self.user1_id = 1
        self.chat1_id = 2
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.db = db

    def tearDown(self):
        pass

    def test_add_user_chat_if_not_exists_combination_does_not_exist(self):
        result = self.service.add_user_chat_if_not_exists(self.user1_id, self.chat1_id)
        self.assertEqual(True, result)
        stats = self.service.get_stats()
        expected = {'num_users': 1, 'num_chats': 1}
        self.assertEqual(expected, stats)

    def test_add_user_chat_if_not_exists_combination_exists(self):
        result = self.service.add_user_chat_if_not_exists(self.user1_id, self.chat1_id)
        self.assertEqual(True, result)
        result = self.service.add_user_chat_if_not_exists(self.user1_id, self.chat1_id)
        self.assertEqual(False, result)
        stats = self.service.get_stats()
        expected = {'num_users': 1, 'num_chats': 1}
        self.assertEqual(expected, stats)

    def test_remove_user_chat_if_exists_combination_exists(self):
        self.service.add_user_chat_if_not_exists(self.user1_id, self.chat1_id)
        result = self.service.remove_user_chat_if_exists(self.user1_id, self.chat1_id)
        self.assertEqual(True, result)
        expected = {'num_users': 0, 'num_chats': 0}
        self.assertEqual(expected, self.service.get_stats())

    def test_remove_user_chat_if_exists_combination_does_not_exist(self):
        result = self.service.remove_user_chat_if_exists(self.user1_id, self.chat1_id)
        self.assertEqual(False, result)

    def test_get_chat_users(self):
        self.service.add_user_chat_if_not_exists(1, 3)
        self.service.add_user_chat_if_not_exists(2, 3)
        self.service.add_user_chat_if_not_exists(2, 4)
        users = self.service.get_chat_users(3)
        self.assertEqual(2, len(users))

    def test_get_chats_of_user(self):
        self.service.add_user_chat_if_not_exists(1, 3)
        self.service.add_user_chat_if_not_exists(2, 3)
        self.service.add_user_chat_if_not_exists(2, 4)
        self.service.add_user_chat_if_not_exists(3, 6)
        users = self.service.get_chats_of_user(2)
        self.assertEqual(2, len(users))

    def test_get_all_users(self):
        self.service.add_user_chat_if_not_exists(1, 3)
        self.service.add_user_chat_if_not_exists(2, 3)
        self.service.add_user_chat_if_not_exists(2, 4)
        users = self.service.get_all_users()
        self.assertEqual(2, len(users))

    def test_get_all_chats(self):
        self.service.add_user_chat_if_not_exists(1, 3)
        self.service.add_user_chat_if_not_exists(2, 3)
        self.service.add_user_chat_if_not_exists(2, 4)
        self.service.add_user_chat_if_not_exists(3, 6)
        chats = self.service.get_all_chats()
        self.assertEqual(3, len(chats))

    def test_get_stats_no_users(self):
        stats = self.service.get_stats()
        expected = {'num_users': 0, 'num_chats': 0}
        self.assertEqual(expected, stats)

    def test_get_stats_users_exist(self):
        self.service.add_user_chat_if_not_exists(1, 3)
        self.service.add_user_chat_if_not_exists(1, 2)
        stats = self.service.get_stats()
        expected = {'num_users': 1, 'num_chats': 2}
        self.assertEqual(expected, stats)


if __name__ == '__main__':
    unittest.main()
