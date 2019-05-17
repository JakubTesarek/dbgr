import functools
from dbgr.requests import register_request

def request(request):
    @functools.wraps(request)
    async def wrapper_decorator(*args, **kwargs):
        await request(*args, **kwargs)
    register_request(wrapper_decorator)
    return wrapper_decorator
