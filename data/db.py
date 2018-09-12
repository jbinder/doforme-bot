from datetime import datetime

from pony.orm import Database, Required, Optional

db = Database()


class UserChat(db.Entity):
    user_id = Required(int)
    chat_id = Required(int)


# class UserSchedule(db.Entity):
#     user_id = Required(int)
#     chat_id = Required(int)


class Task(db.Entity):
    user_id = Required(int)
    chat_id = Required(int)
    owner_id = Required(int)
    title = Required(str)
    created = Required(datetime)
    done = Optional(datetime)
    due = Optional(datetime)


class Feedback(db.Entity):
    user_id = Required(int)
    created = Required(datetime)
    text = Required(str)
    done = Optional(datetime)


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

