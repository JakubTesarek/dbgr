import inspect
import os
import functools
import importlib.util
import glob
import colorama
from dbgr.environment import get_environment
from dbgr.session import get_session
from dbgr.types import Type
from dbgr.arguments import DefaultValueArgument, NoDefaultValueArgument
from dbgr.results import Result


_REQUESTS = None
_CACHE = {}


class RequestNotFoundError(ValueError):
    pass


class RequestNotImplementsError(RequestNotFoundError):
    pass


class AmbiguousRequestNameError(RequestNotFoundError):
    pass


class InvalidRequestNameError(ValueError):
    pass


class DuplicateRequestNameError(ValueError):
    pass


class Request:
    env_arg = 'env'
    session_arg = 'session'

    def __init__(self, request, name=None, cache=None):
        self.name = name if name is not None else request.__name__
        self.request = request
        self.cache = cache
        self.validate_name()
        self.annotation = Type.get_type(self.request.__annotations__.get('return'))

    @property
    def module(self):
        return self.request.__module__

    @property
    def doc(self):
        if self.request.__doc__ is not None:
            return self.request.__doc__.strip()
        return ''

    @property
    def extra_arguments(self):
        extras = []
        args_spec = inspect.getfullargspec(self.request)
        args = args_spec.args
        if self.env_arg in args:
            args.remove(self.env_arg)
        if self.session_arg in args:
            args.remove(self.session_arg)
        defaults = list(args_spec.defaults or [])
        for argument in args[::-1]:
            annotation = Type.get_type(args_spec.annotations.get(argument))
            if defaults:
                arg = DefaultValueArgument(argument, annotation, defaults.pop())
            else:
                arg = NoDefaultValueArgument(argument, annotation)
            extras.append(arg)
        return extras[::-1]

    @property
    def requires_env(self):
        args_spec = inspect.getfullargspec(self.request)
        return self.env_arg in args_spec.args[:2]

    @property
    def requires_session(self):
        args_spec = inspect.getfullargspec(self.request)
        return self.session_arg in args_spec.args[:2]

    def resolve_arguments(self, env, session, use_defaults, kwargs):
        arguments = {}
        for argument in self.extra_arguments:
            arguments[argument.name] = argument.get_value(
                kwargs, use_default=use_defaults
            )
        if self.requires_env:
            arguments[self.env_arg] = env
        if self.requires_session:
            arguments[self.session_arg] = session
        return arguments

    def cache_key(self, arguments):
        key = set((self.name, self.module))
        for name, value in arguments.items():
            if name not in (self.env_arg, self.session_arg):
                key.add((name, value))
        return frozenset(key)

    async def __call__(self, env, session, use_defaults=False, cache=True, kwargs=None): # pylint: disable=R0913
        kwargs = {} if kwargs is None else kwargs
        arguments = self.resolve_arguments(env, session, use_defaults, kwargs)
        if self.cache:
            cached = True
            key = self.cache_key(arguments)
            if key not in _CACHE or not cache:
                cached = False
                _CACHE[key] = await self.request(**arguments)
            return Result(_CACHE[key], self.annotation, cached)
        value = await self.request(**arguments)
        return Result(value, self.annotation)

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

    def __str__(self):
        buff = f'- {self.name}\n'
        if self.annotation or self.cache:
            buff_1, buff_2 = '', ''
            if self.cache:
                buff_1 = f'cache: {self.cache}'
            if self.annotation:
                buff_2 = f'return: {self.annotation}'
            buff += f'  {colorama.Style.DIM}[{buff_1}{", " if buff_1 and buff_2 else ""}{buff_2}]\n'
        if self.doc:
            buff += f'  {colorama.Style.DIM}{self.doc}\n'
        if self.extra_arguments:
            buff += f'  {colorama.Style.DIM}Arguments:\n'
            for argument in self.extra_arguments:
                buff += f'   {colorama.Style.DIM}- {argument}\n'
        return buff


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
        request, env=None, session=None, use_defaults=False, cache=True, **kwargs):
    env = env if env is not None else get_environment()
    session = session if session is not None else get_session()
    request = find_request(request)
    result = await request(
        env, session, use_defaults=use_defaults, cache=cache, kwargs=kwargs)
    print(result)
    return result.value


def extract_module_name(module_path):
    return os.path.splitext(os.path.basename(module_path))[0]


def load_module(module_path):
    module_name = extract_module_name(module_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def load_requests():
    global _REQUESTS # pylint: disable=W0603
    _REQUESTS = {}
    for module_path in glob.glob(f'{os.getcwd()}/*.py'):
        load_module(module_path)


def register_request(request):
    if request.module not in _REQUESTS:
        _REQUESTS[request.module] = {}
    _REQUESTS[request.module][request.name] = request


def find_request(request_name):
    module, request = parse_request_name(request_name)
    requests = get_requests()
    if module:
        if module not in requests:
            raise RequestNotImplementsError(f'Module "{module}" does not exist.')
        if request not in requests[module]:
            raise RequestNotImplementsError(f'Request "{request_name}" does not exist.')
        return requests[module][request]

    adepts = set()
    for _, requests in requests.items():
        for _, adept in requests.items():
            if adept.name == request:
                adepts.add(adept)
    if len(adepts) == 1:
        return adepts.pop()
    if not adepts:
        raise RequestNotImplementsError(f'Request "{request_name}" does not exist')
    raise AmbiguousRequestNameError(
        f'Request "{request_name}" found in multiple modules: '
        f'{", ".join([r.module for r in adepts])}'
    )


def parse_module_name(module):
    request = None
    if module and ':' in module:
        module, request = module.split(':', 1)
    return None if module == '' else module, request


def parse_request_name(request):
    module = None
    if request and ':' in request:
        module, request = request.split(':', 1)
    return None if module == '' else module, None if request == '' else request


def request_decorator(name=None, cache=None):
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
