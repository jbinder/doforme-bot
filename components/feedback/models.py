from datetime import datetime

from pony.orm import Required, Optional

from common.utils.db_tools import get_database, init_database

db = get_database()


class Feedback(db.Entity):
    user_id = Required(int)
    created = Required(datetime)
    text = Required(str)
    done = Optional(datetime)


init_database(db)
