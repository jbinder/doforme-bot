from datetime import datetime

from pony.orm import commit, db_session, select

from components.user.models import UserChat, db, User, Chat
from common.decorators.db_use_utf8mb import db_use_utf8mb
from common.decorators.retry_on_error import retry_on_error


class UserService:
    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def add_user_if_not_exists(self, user_id):
        """ :returns True if added, False if already exists """
        if not User.get(user_id=user_id):
            User(user_id=user_id, created_at=datetime.utcnow(), is_active=True)
            commit()
            return True
        return False

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def add_chat_if_not_exists(self, chat_id):
        """ :returns True if added, False if already exists """
        if not Chat.get(chat_id=chat_id):
            Chat(chat_id=chat_id, created_at=datetime.utcnow(), is_active=True)
            commit()
            return True
        return False

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def add_user_chat_if_not_exists(self, user_id, chat_id):
        """ :returns True if added, False if already exists """
        if not UserChat.get(user_id=user_id, chat_id=chat_id):
            UserChat(user_id=user_id, chat_id=chat_id)
            commit()
            return True
        return False

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def remove_user_chat_if_exists(self, user_id, chat_id):
        """ :returns True if removed, False if not exists """
        user_chat = UserChat.get(user_id=user_id, chat_id=chat_id)
        if user_chat:
            user_chat.delete()
            commit()
            return True
        return False

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def remove_chat_if_exists(self, chat_id):
        """ :returns True if removed, False if not exists """
        chat = Chat.get(chat_id=chat_id)
        if chat:
            chat.delete()
            commit()
            return True
        return False

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def get_chat_users(self, chat_id):
        # noinspection PyTypeChecker
        return select(user_chat.user_id for user_chat in UserChat if user_chat.chat_id == chat_id)[:]

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def get_chats_of_user(self, user_id):
        # noinspection PyTypeChecker
        return select(user_chat.chat_id for user_chat in UserChat if user_chat.user_id == user_id)[:]

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def get_all_users(self):
        # noinspection PyTypeChecker
        return select(user_chat.user_id for user_chat in UserChat)[:]

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def get_all_chats(self):
        # noinspection PyTypeChecker
        return select(user_chat.chat_id for user_chat in UserChat)[:]

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def get_stats(self):
        # noinspection PyTypeChecker
        return {
            'num_users': select(user_chat.user_id for user_chat in UserChat).count(True),
            'num_chats': select(user_chat.chat_id for user_chat in UserChat).count(True),
        }

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def report_user_send_failure(self, event):
        user_id = event['user_id']
        if not User.exists(user_id=user_id):
            self.add_user_if_not_exists(user_id)
        user = User.get(user_id=user_id)
        user.last_error_at = datetime.utcnow()
        user.error_message = event['exception'].message
        user.is_active = False
        commit()

    @db_session
    @db_use_utf8mb(db)
    @retry_on_error
    def report_chat_send_failure(self, event):
        chat_id = event['chat_id']
        if not Chat.exists(chat_id=chat_id):
            self.add_chat_if_not_exists(chat_id)
        chat = Chat.get(chat_id=chat_id)
        chat.last_error_at = datetime.utcnow()
        chat.error_message = event['exception'].message
        chat.is_active = False
        commit()
