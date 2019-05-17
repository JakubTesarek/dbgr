import functools
from dbgr.requests import register_request


def request(name=None):
    func = name
    if callable(func):
        register_request(func)
        return func
    else:
        @functools.wraps(func)
        def decorator(func):
            if name is not None:
                func.__name__ = name
            register_request(func)
            return func
        return decorator
