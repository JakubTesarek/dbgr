import functools
from dbgr.requests import register_request, execute_request, Request


async def response(request, env, session, **kwargs):
    return await execute_request(session, env, request, **kwargs)


def request(name=None, cache=None):
    func = name
    if callable(func):
        request = Request(func)
        register_request(request)
        return request
    @functools.wraps(func)
    def decorator(func):
        request = Request(func, name, cache)
        register_request(request)
        return request
    return decorator
