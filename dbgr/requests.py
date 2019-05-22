import inspect
import colorama
import os
import importlib.util
import glob
from dataclasses import dataclass
from pprint import pprint

_REQUESTS = None
_CACHE = {}

class RequestNotFoundError(ValueError): pass
class RequestNotImplementsError(RequestNotFoundError): pass
class AmbiguousRequestNameError(RequestNotFoundError): pass
class InvalidRequestNameError(ValueError): pass
class DuplicateRequestNameError(ValueError): pass


@dataclass
class Result:
    value: object
    cached: bool = False

    def print(self):
        if self.value is not None:
            if self.cached:
                print(
                    f'{colorama.Style.BRIGHT}Result{colorama.Style.RESET_ALL} '
                    f'{colorama.Style.DIM}({type(self.value).__name__}, from cache)'
                    f'{colorama.Style.RESET_ALL}:'
                )
            else:
                print(
                    f'{colorama.Style.BRIGHT}Result{colorama.Style.RESET_ALL} '
                    f'{colorama.Style.DIM}({type(self.value).__name__})'
                    f'{colorama.Style.RESET_ALL}:'
                )
            pprint(self.value)


class Argument:
    def __init__(self, name):
       self.name = name

    def __str__(self):
        return self.name


class NoDefaultValueArgument(Argument):
    def get_value(self, kwargs, use_default=None):
        if self.name in kwargs:
            return kwargs[self.name]
        value = input(f'{self}: ')
        return value


class DefaultValueArgument(Argument):
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def __str__(self):
        return f'{self.name} [{self.value}]'

    def get_value(self, kwargs, use_default=False):
        if self.name in kwargs:
            return kwargs[self.name]
        if use_default == True:
            return self.value
        value = input(f'{self}: ')
        if value == '':
            value = self.value
        return value


class Request:
    def __init__(self, request, name=None, cache=None):
        self.name = name if name is not None else request.__name__
        self.request = request
        self.validate_name()
        self.cache = cache

    @property
    def module(self):
        return self.request.__module__

    @property
    def doc(self):
        if self.request.__doc__ is not None:
            return self.request.__doc__.strip()

    @property
    def extra_arguments(self):
        extras = []
        args_spec = inspect.getargspec(self.request)
        defaults = list(args_spec.defaults or [])
        for argument in args_spec.args[:1:-1]:
            if defaults:
                extras.append(DefaultValueArgument(argument, defaults.pop()))
            else:
                extras.append(NoDefaultValueArgument(argument))
        return extras[::-1]

    def resolve_arguments(self, use_defaults, kwargs):
        arguments = {}
        for argument in self.extra_arguments:
            arguments[argument.name] = argument.get_value(
                kwargs, use_default=use_defaults
            )
        return arguments

    async def __call__(
        self, env, session, use_defaults=False, cache=True, kwargs={}
    ):
        arguments = self.resolve_arguments(use_defaults, kwargs)
        if self.cache:
            cached = True
            key = (self.name, self.module, frozenset(arguments))
            if key not in _CACHE or cache == False:
                cached = False
                _CACHE[key] = await self.request(env, session, **arguments)
            return Result(_CACHE[key], cached)
        value = await self.request(env, session, **arguments)
        return Result(value)

    def validate_name(self):
        if not self.name.isidentifier():
            raise InvalidRequestNameError(
                f'"{self.module}:{self.name}" is not valid request identifier. '
                f'Name can containt only letters, numbers and/or underscore'
            )
        if self.name in get_requests().get(self.module, set()):
            raise DuplicateRequestNameError(
                f'"{self.name}" is already defined in module {self.module}'
            )


def get_requests():
    if _REQUESTS is None:
        load_requests()
    return _REQUESTS


def parse_cmd_arguments(args):
    result = {}
    for arg in args:
        parsed = arg.split('=', 1)
        if len(parsed) == 1:
            result[arg] = True
        else:
            result[parsed[0]] = parsed[1]
    return result


async def execute_request(
    session, environment, request, use_defaults=False, cache=True, **kwargs
):
    request = find_request(request)
    result = await request(
        environment, session, use_defaults=use_defaults, cache, kwargs=kwargs)
    result.print()
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
