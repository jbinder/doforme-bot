import functools

from common.utils.db_tools import use_mysql


def db_use_utf8mb(db):
    """ Sets the character set to utf8mb (MySQL only). Add after the Pony db_session decorator. """

    def decorator_db_use_utf8mb(f):
        @functools.wraps(f)
        def decorator(*args, **kw):
            if use_mysql():
                # note: this must be done within a Pony session!
                db.execute("SET NAMES utf8mb4;")
            return f(*args, **kw)

        return decorator

    return decorator_db_use_utf8mb
