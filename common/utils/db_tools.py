import os

from pony.orm import Database


def get_database():
    return Database()


def init_database(db):
    if use_mysql():
        host = os.environ.get('DFM_DB_HOST', 'localhost')
        port = int(os.environ.get('DFM_DB_PORT', 3306))
        username = os.environ['DFM_DB_USERNAME']
        password = os.environ['DFM_DB_PASSWORD']
        database = os.environ['DFM_DB_DATABASE']
        db.bind(provider='mysql', host=host, user=username, passwd=password, db=database, port=port)
        db.execute("SET NAMES utf8mb4;")
    elif 'DFM_ENV' in os.environ and os.environ['DFM_ENV'] is 'Test':
        db.bind(provider='sqlite', filename=':memory:')
    else:
        # use sqlite as fallback
        db.bind(provider='sqlite', filename='database.sqlite', create_db=True)

    db.generate_mapping(create_tables=True)


def use_mysql():
    return 'DFM_DB_USERNAME' in os.environ
