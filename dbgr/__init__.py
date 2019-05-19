import functools
from dbgr.requests import register_request, execute_request


async def response(request, env, session):
    return await execute_request(session, env, request)


def request(name=None):
    func = name
    if callable(func):
        func.name = func.__name__
        func.module = func.__module__
        register_request(func)
        return func
    else:
        @functools.wraps(func)
        def decorator(func):
            if name is not None:
                func.name = name if name is not None else func.__name__
            func.module = func.__module__
            register_request(func)
            return func
        return decorator
