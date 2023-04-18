from datetime import datetime

from pony.orm import Required, Optional

from common.utils.db_tools import get_database, init_database

db = get_database()


class UserChat(db.Entity):
    user_id = Required(int, size=64)
    chat_id = Required(int, size=64)


class User(db.Entity):
    user_id = Required(int, size=64)
    created_at = Required(datetime)
    deleted_at = Optional(datetime)
    is_active = Required(bool)
    last_error_at = Optional(datetime)
    error_message = Optional(str)


class Chat(db.Entity):
    chat_id = Required(int, size=64)
    created_at = Required(datetime)
    deleted_at = Optional(datetime)
    is_active = Required(bool)
    last_error_at = Optional(datetime)
    error_message = Optional(str)


init_database(db)
