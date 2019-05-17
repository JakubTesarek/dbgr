import os
import importlib.util
import glob

REQUESTS = None


def get_requests_list():
    if REQUESTS is None:
        load_requests()
    return REQUESTS


async def execute_request(session, environment, request):
    request = find_request(request)
    async with session as s:
        await request(environment.env, s)


def extract_module_name(module_path):
    return os.path.splitext(os.path.basename(module_path))[0]


def load_module(module_path):
    module_name = extract_module_name(module_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def load_requests():
    global REQUESTS
    REQUESTS = set()
    for module_path in glob.glob(f'{os.getcwd()}/*.py'):
        load_module(module_path)


def register_request(request):
    REQUESTS.add(request)


def find_request(request_name):
    name = request_name
    module = None
    if ':' in name:
       module, name = name.split(':', 1)

    adepts = set()
    for r in REQUESTS:
        if r.__name__ == name:
            if r.__module__ == module:
                return r
            elif module is None:
                adepts.add(r)
    if len(adepts) == 1:
        return adepts.pop()
    if len(adepts) == 0:
        raise Exception(f'Request {request_name} was not found')
    raise Exception(f'Found multipte requests for name {request_name}')
