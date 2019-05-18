import os
import importlib.util
import glob

_REQUESTS = None
_REQUESTS_NAMES = {}

class RequestNotFoundError(ValueError): pass
class RequestNotImplementsError(RequestNotFoundError): pass
class AmbiguousRequestNameError(RequestNotFoundError): pass
class InvalidRequestNameError(ValueError): pass
class DuplicateRequestNameError(ValueError): pass


def validate_request_name(request):
    if not request.__name__.isidentifier():
        raise InvalidRequestNameError(
            f'"{request.__module__}:{request.__name__}" is not valid request identifier. '
            f'Name can containt only letters, numbers and/or underscore'
        )
    if request.__name__ in get_requests_names().get(request.__module__, set()):
        raise DuplicateRequestNameError(
            f'"{request.__name__}" is already defined in module {request.__module__}'
        )


def get_requests():
    if _REQUESTS is None:
        load_requests()
    return _REQUESTS

def get_requests_names():
    if _REQUESTS is None:
        load_requests()
    return _REQUESTS_NAMES


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
    global _REQUESTS
    _REQUESTS = set()
    for module_path in glob.glob(f'{os.getcwd()}/*.py'):
        load_module(module_path)


def register_request(request):
    validate_request_name(request)
    _REQUESTS.add(request)
    if request.__module__ not in _REQUESTS_NAMES:
        _REQUESTS_NAMES[request.__module__] = set()
    _REQUESTS_NAMES[request.__module__].add(request.__name__)


def find_request(request_name):
    name = request_name
    module = None
    if ':' in name:
       module, name = name.split(':', 1)

    adepts = set()
    for r in get_requests():
        if r.__name__ == name:
            if r.__module__ == module:
                return r
            elif module is None:
                adepts.add(r)
    if len(adepts) == 1:
        return adepts.pop()
    if len(adepts) == 0:
        raise RequestNotImplementsError(f'Request "{request_name}" was not found.')
    raise AmbiguousRequestNameError(
        f'Request "{request_name}" found in multiple modules: '
        f'{", ".join([r.__module__ for r in adepts])}'
    )
