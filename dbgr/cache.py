import functools

_CACHE = {}


def cache_request(request, cache_type):
    if cache_type is not None:
        if cache_type != 'session':
            raise ValueError(f'Unknown cache type "{cache_type}", must be: session')
        @functools.wraps(request)
        async def cache_decorator(*args, **kwargs):
            if request not in _CACHE:
                _CACHE[request] = await request(*args, **kwargs)
            else:
                _CACHE[request].cached = True 
            return _CACHE[request]
        return cache_decorator
    return request
