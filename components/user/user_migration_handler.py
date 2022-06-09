from pony.orm import select, commit, db_session

from common.decorators.db_use_utf8mb import db_use_utf8mb
from common.migration_handler_base import MigrationHandlerBase
from components.user.models import UserChat, db


class UserMigrationHandler(MigrationHandlerBase):

    @db_session
    @db_use_utf8mb(db)
    def migrate_to_supergroup(self, chat_id: int, new_chat_id: int):
        # noinspection PyTypeChecker
        user_chats = select(user_chat for user_chat in UserChat if user_chat.chat_id == chat_id)[:]
        for user_chat in user_chats:
            user_chat.chat_id = new_chat_id
        commit()

