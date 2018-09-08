import functools


def ensure_exec_sequence(previous):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            doforme_bot = args[0]
            if not hasattr(doforme_bot, 'last_method_called'):
                raise RuntimeError("This decorator needs to be attached to methods of the DoForMeBot!")
            if not previous or doforme_bot.last_method_called == previous:
                doforme_bot.last_method_called = func.__name__
                return func(*args, **kwargs)

        return wrapper

    return decorator
