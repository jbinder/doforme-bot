from pony.orm import Database, Required

db = Database()


class UserChat(db.Entity):
    user_id = Required(int)
    chat_id = Required(int)


class Task(db.Entity):
    user_id = Required(int)
    chat_id = Required(int)
    owner_id = Required(int)
    title = Required(str)


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

