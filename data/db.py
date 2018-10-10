import os
from datetime import datetime

from pony.orm import Database, Required, Optional, db_session

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


if 'DFM_DB_USERNAME' in os.environ:
    # use mysql
    host = os.environ.get('DFM_DB_HOST', 'localhost')
    port = int(os.environ.get('DFM_DB_PORT', 3306))
    username = os.environ['DFM_DB_USERNAME']
    password = os.environ['DFM_DB_PASSWORD']
    database = os.environ['DFM_DB_DATABASE']
    db.bind(provider='mysql', host=host, user=username, passwd=password, db=database, port=port)
elif 'DFM_ENV' in os.environ and os.environ['DFM_ENV'] is 'Test':
    db.bind(provider='sqlite', filename=':memory:')
else:
    # use sqlite as fallback
    db.bind(provider='sqlite', filename='database.sqlite', create_db=True)

db.generate_mapping(create_tables=True)
