import functools

from data import db


def db_use_utf8mb(f):
    """ Sets the character set to utf8mb (MySQL only). Add after the db_session decorator. """

    @functools.wraps(f)
    def decorator(*args, **kw):
        if db.db.provider_name == "mysql":
            db.db.execute("SET NAMES utf8mb4;")
        return f(*args, **kw)

    return decorator
