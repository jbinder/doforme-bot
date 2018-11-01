from pony.orm import commit, db_session, select

from components.user.models import UserChat, db
from common.decorators.db_use_utf8mb import db_use_utf8mb
from common.decorators.retry_on_error import retry_on_error


class UserService:
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
