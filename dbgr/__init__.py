import functools
import os
import importlib.util


REQUESTS = set()


def load_requests(filename):
    cwd = os.getcwd()
    spec = importlib.util.spec_from_file_location('requests', f'{cwd}/{filename}'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def request(request):
    @functools.wraps(request)
    async def wrapper_decorator(*args, **kwargs):
        await request(*args, **kwargs)
    REQUESTS.add(wrapper_decorator)
    return wrapper_decorator
