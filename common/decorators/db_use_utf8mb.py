import functools

from common.utils.db_tools import use_mysql


def db_use_utf8mb(f):
    """ Sets the character set to utf8mb (MySQL only). Add after the db_session decorator. """

    @functools.wraps(f)
    def decorator(*args, **kw):
        if use_mysql():
            db.execute("SET NAMES utf8mb4;")
        return f(*args, **kw)

    return decorator
