import inspect
import os
import importlib.util
import glob
from dataclasses import dataclass
from pprint import pformat
import colorama


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


class Type:
    supported_types = ['bool', 'str', 'int', 'float']

    def __init__(self, cls):
        self.cls = None
        if cls and cls.__name__ in self.supported_types:
            self.cls = cls

    def cast(self, value):
        if value is not None and self:
            if self.cls == bool:
                if isinstance(value, str):
                    value = value.lower()
                return value not in [0, 0.0, '0', False, 'f', 'false', 'n', 'no']
            return self.cls(value)
        return value

    def __str__(self):
        if self:
            return self.cls.__name__
        return ''

    def __bool__(self):
        return self.cls is not None


@dataclass
class Result:
    _value: object
    annotation: Type
    cached: bool = False

    def __str__(self):
        from_cache = ''
        if self.cached:
            from_cache = ', from cache'
        buffer = (
            f'{colorama.Style.BRIGHT}Result{colorama.Style.RESET_ALL} '
            f'{colorama.Style.DIM}({type(self.value).__name__}{from_cache})'
        )
        if self.value is not None:
            buffer += f'{colorama.Style.RESET_ALL}:\n{pformat(self.value)}'
        return buffer

    @property
    def value(self):
        return self.annotation.cast(self._value)


class Argument:
    def __init__(self, name, annotation):
        self.name = name
        self.annotation = annotation

    def __str__(self):
        if self.annotation:
            return f'{self.name} [type: {self.annotation}]'
        return self.name

    def cast(self, value):
        try:
            return self.annotation.cast(value)
        except:
            print(f'{colorama.Fore.RED}String "{value}" cannot be converted to {self.annotation}')
            raise

    def value_input(self, nullable=False):
        value = input(f'{self}: ')
        if nullable and value == '':
            return None
        try:
            return self.cast(value)
        except ValueError:
            return self.value_input(nullable)


class NoDefaultValueArgument(Argument):
    def get_value(self, kwargs, use_default=None): # pylint: disable=W0613
        if self.name in kwargs:
            return self.cast(kwargs[self.name])
        return self.value_input()


class DefaultValueArgument(Argument):
    def __init__(self, name, annotation, value):
        super().__init__(name, annotation)
        self.value = value

    def __str__(self):
        if self.annotation:
            return f'{self.name} [default: {self.value}, type: {self.annotation}]'
        return f'{self.name} [default: {self.value}]'

    def get_value(self, kwargs, use_default=False):
        if self.name in kwargs:
            value = self.cast(kwargs[self.name])
        elif use_default:
            value = self.value
        else:
            value = self.value_input(nullable=True)
            if value is None:
                value = self.value
        return value


class Request:
    def __init__(self, request, name=None, cache=None):
        self.name = name if name is not None else request.__name__
        self.request = request
        self.cache = cache
        self.validate_name()
        self.annotation = Type(self.request.__annotations__.get('return'))

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
        defaults = list(args_spec.defaults or [])
        for argument in args_spec.args[:1:-1]:
            annotation = Type(args_spec.annotations.get(argument))
            if defaults:
                arg = DefaultValueArgument(argument, annotation, defaults.pop())
            else:
                arg = NoDefaultValueArgument(argument, annotation)
            extras.append(arg)
        return extras[::-1]

    def resolve_arguments(self, use_defaults, kwargs):
        arguments = {}
        for argument in self.extra_arguments:
            arguments[argument.name] = argument.get_value(
                kwargs, use_default=use_defaults
            )
        return arguments

    async def __call__(self, env, session, use_defaults=False, cache=True, kwargs=None): # pylint: disable=R0913
        kwargs = {} if kwargs is None else kwargs
        arguments = self.resolve_arguments(use_defaults, kwargs)
        if self.cache:
            cached = True
            key = (self.name, self.module, frozenset(arguments.items()))
            if key not in _CACHE or not cache:
                cached = False
                _CACHE[key] = await self.request(env, session, **arguments)
            return Result(_CACHE[key], self.annotation, cached)
        value = await self.request(env, session, **arguments)
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
        session, environment, request, use_defaults=False, cache=True, **kwargs):
    request = find_request(request)
    result = await request(
        environment, session, use_defaults=use_defaults, cache=cache, kwargs=kwargs)
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
    request = request_name
    module = None
    if ':' in request:
        module, request = request.split(':', 1)

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
