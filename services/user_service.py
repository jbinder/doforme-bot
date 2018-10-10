from pony.orm import commit, db_session, select

# from data.db import UserChat, UserSchedule
from data.db import UserChat
from decorators.db_use_utf8mb import db_use_utf8mb


class UserService:
    @db_session
    @db_use_utf8mb
    def add_user_chat_if_not_exists(self, user_id, chat_id):
        """ :returns True if added, False if already exists """
        if not UserChat.get(user_id=user_id, chat_id=chat_id):
            UserChat(user_id=user_id, chat_id=chat_id)
            commit()
            return True
        return False

    @db_session
    @db_use_utf8mb
    def remove_user_chat_if_exists(self, user_id, chat_id):
        """ :returns True if removed, False if not exists """
        user_chat = UserChat.get(user_id=user_id, chat_id=chat_id)
        if user_chat:
            user_chat.delete()
            commit()
            return True
        return False

    @db_session
    @db_use_utf8mb
    def get_chat_users(self, chat_id):
        # noinspection PyTypeChecker
        return select(user_chat.user_id for user_chat in UserChat if user_chat.chat_id == chat_id)[:]

    @db_session
    @db_use_utf8mb
    def get_chats_of_user(self, user_id):
        # noinspection PyTypeChecker
        return select(user_chat.chat_id for user_chat in UserChat if user_chat.user_id == user_id)[:]

    @db_session
    @db_use_utf8mb
    def get_all_users(self):
        # noinspection PyTypeChecker
        return select(user_chat.user_id for user_chat in UserChat)[:]

    @db_session
    @db_use_utf8mb
    def get_all_chats(self):
        # noinspection PyTypeChecker
        return select(user_chat.chat_id for user_chat in UserChat)[:]

    @db_session
    @db_use_utf8mb
    def get_stats(self):
        # noinspection PyTypeChecker
        return {
            'num_users': select(user_chat.user_id for user_chat in UserChat).count(True),
            'num_chats': select(user_chat.chat_id for user_chat in UserChat).count(True),
        }

    # @db_session
    # def add_user_schedule_if_not_exists(self, user_id, chat_id):
    #     """ :returns True if added, False if already exists """
    #     if not UserSchedule.get(user_id=user_id, chat_id=chat_id):
    #         UserSchedule(user_id=user_id, chat_id=chat_id)
    #         commit()
    #         return True
    #     return False
    #
    # @db_session
    # def remove_user_schedule_if_exists(self, user_id, chat_id):
    #     """ :returns True if removed, False if not exists """
    #     user_schedule = UserSchedule.get(user_id=user_id, chat_id=chat_id)
    #     if user_schedule:
    #         user_schedule.delete()
    #         commit()
    #         return True
    #     return False
    #
    # @db_session
    # def get_all_user_schedules(self):
    #     return select(user_schedule for user_schedule in UserSchedule)[:]
