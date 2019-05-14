import functools
import os
import importlib.util
import glob


REQUESTS = set()

def load_requests():
    for module_path in glob.glob(f'{os.getcwd()}/*.py'):
        print(module_path)
        load_module(module_path)


def load_module(module_path):
    spec = importlib.util.spec_from_file_location('requests', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def request(request):
    @functools.wraps(request)
    async def wrapper_decorator(*args, **kwargs):
        await request(*args, **kwargs)
    REQUESTS.add(wrapper_decorator)
    return wrapper_decorator
