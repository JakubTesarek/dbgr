import functools
from dbgr.requests import register_request, execute_request, Result
from dbgr.cache import cache_request


def request_executor(request):
    @functools.wraps(request)
    async def dec(*args, **kwargs):
        r = await request(*args, **kwargs)
        result = Result(r)
        return result
    return dec
    

async def response(request, env, session):
    return await execute_request(session, env, request)


def name_request(request, name=None):
    request.name = name if name is not None else request.__name__
    request.module = request.__module__
    return request


def request(name=None, cache=None):
    func = name
    if callable(func):
        func = request_executor(func)
        func = name_request(func)
        register_request(func)
        return func
    else:
        @functools.wraps(func)
        def decorator(func):
            func = request_executor(func)
            func = cache_request(func, cache)
            func = name_request(func, name)
            register_request(func)
            return func
        return decorator
