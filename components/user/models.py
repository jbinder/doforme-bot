from pony.orm import Required

from common.utils.db_tools import get_database, init_database

db = get_database()


class UserChat(db.Entity):
    user_id = Required(int, size=64)
    chat_id = Required(int, size=64)


init_database(db)
