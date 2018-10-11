import functools

from pony.orm import OperationalError


def retry_on_error(f):
    """ Try executing methods second time on specific errors (i.e. timeouts). """

    @functools.wraps(f)
    def decorator(*args, **kw):
        try:
            return f(*args, **kw)
        except OperationalError:
            # retry once
            return f(*args, **kw)

    return decorator
