from datetime import datetime

from pony.orm import Required, Optional

from common.utils.db_tools import get_database, init_database

db = get_database()


class Task(db.Entity):
    user_id = Required(int, size=64)
    chat_id = Required(int, size=64)
    owner_id = Required(int, size=64)
    title = Required(str)
    created = Required(datetime)
    done = Optional(datetime)
    due = Optional(datetime)
    description = Optional(str)
    is_group_task = Required(bool)


init_database(db)
