import colorama
import os
import importlib.util
import glob
from dataclasses import dataclass

_REQUESTS = None

class RequestNotFoundError(ValueError): pass
class RequestNotImplementsError(RequestNotFoundError): pass
class AmbiguousRequestNameError(RequestNotFoundError): pass
class InvalidRequestNameError(ValueError): pass
class DuplicateRequestNameError(ValueError): pass


@dataclass
class Result:
    value: object
    cached: bool = False


def validate_request_name(request):
    if not request.name.isidentifier():
        raise InvalidRequestNameError(
            f'"{request.module}:{request.name}" is not valid request identifier. '
            f'Name can containt only letters, numbers and/or underscore'
        )
    if request.name in get_requests().get(request.module, set()):
        raise DuplicateRequestNameError(
            f'"{request.name}" is already defined in module {request.module}'
        )


def get_requests():
    if _REQUESTS is None:
        load_requests()
    return _REQUESTS


async def execute_request(session, environment, request):
    request = find_request(request)
    result = await request(environment, session)
    
    if result.value is None:
        return
    elif result.cached:
        print(f'{colorama.Style.BRIGHT}Result{colorama.Style.RESET_ALL} (from cache):')
    else:
        print(f'{colorama.Style.BRIGHT}Result:')
    print(result.value)
    return result.value

def extract_module_name(module_path):
    return os.path.splitext(os.path.basename(module_path))[0]


def load_module(module_path):
    module_name = extract_module_name(module_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def load_requests():
    global _REQUESTS
    _REQUESTS = {}
    for module_path in glob.glob(f'{os.getcwd()}/*.py'):
        load_module(module_path)


def register_request(request):
    validate_request_name(request)
    if request.module not in _REQUESTS:
        _REQUESTS[request.module] = {}
    _REQUESTS[request.module][request.name] = request


def find_request(request_name):
    request = request_name
    module = None
    if ':' in request:
       module, request = name.split(':', 1)

    requests = get_requests()
    if module:
        if module not in requests:
            raise RequestNotImplementsError(f'Module "{module}" does not exist.')
        if request not in requests[module]:
            raise RequestNotImplementsError(f'Request "{request_name}" does not exist.')
        return requests[module][request]
    else:
        adepts = set()
        for _, requests in requests.items():
            for _, r in requests.items():
                if r.name == request:
                    if r.module == module:
                        return r
                    elif module is None:
                        adepts.add(r)
        if len(adepts) == 1:
            return adepts.pop()
        if len(adepts) == 0:
            raise RequestNotImplementsError(f'Request "{request_name}" does not exist')
        raise AmbiguousRequestNameError(
            f'Request "{request_name}" found in multiple modules: '
            f'{", ".join([r.module for r in adepts])}'
        )
