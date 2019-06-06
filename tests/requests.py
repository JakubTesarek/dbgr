import random
import pytest
import dbgr.requests
from tests.conftest import escape_ansi
from dbgr.requests import (
    parse_cmd_arguments, get_requests, extract_module_name, Request, find_request,
    RequestNotImplementsError, AmbiguousRequestNameError, register_request,
    parse_module_name, parse_request_name, load_module, load_requests,
    execute_request, request_decorator
)
from dbgr.types import Type, PrimitiveType
from dbgr.results import Result
from dbgr.arguments import DefaultValueArgument, NoDefaultValueArgument
from tests.conftest import mock_request


def test_parse_cmd_arguments_empty():
    assert parse_cmd_arguments([]) == {}


def test_parse_cmd_arguments():
    args = ['arg1=val1', 'arg2=val2']
    assert parse_cmd_arguments(args) == {'arg1': 'val1', 'arg2': 'val2'}


def test_cmd_arguments_without_value_resolved_to_true():
    assert parse_cmd_arguments(['arg1']) == {'arg1': True}


def test_get_requests_loads_requests_once(monkeypatch):
    def mocked_load_requests():
        mocked_load_requests.counter += 1
        monkeypatch.setattr(dbgr.requests, '_REQUESTS', {'module': {}})
    mocked_load_requests.counter = 0
    monkeypatch.setattr(dbgr.requests, 'load_requests', mocked_load_requests)
    assert get_requests() == {'module': {}}
    assert get_requests() == {'module': {}}
    assert mocked_load_requests.counter == 1


@pytest.mark.parametrize('path, name', [
    ('some/path/module.py', 'module'),
    ('../../relative/path.py', 'path'),
    ('simple.py', 'simple'),
    ('with-special_characters.py', 'with-special_characters')
])
def test_extract_module_name(path, name):
    assert extract_module_name(path) == name

def test_find_request_by_name(monkeypatch, mocked_request):
    requests = {mocked_request.module: {mocked_request.name: mocked_request}}
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request(mocked_request.name) == mocked_request


def test_find_request_by_module_and_name(monkeypatch, mocked_request):
    requests = {mocked_request.module: {mocked_request.name: mocked_request}}
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request(f'{mocked_request.module}:{mocked_request.name}') == mocked_request


def test_find_request_by_module_and_duplicit_name(monkeypatch):
    req1 = mock_request(module='module1')
    req2 = mock_request(module='module2')
    requests = {
        req1.module: {req1.name: req1},
        req2.module: {req2.name: req2}
    }
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request(f'{req1.module}:{req2.name}') == req1


def test_find_request_module_doesnt_exist(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    with pytest.raises(RequestNotImplementsError):
        find_request('module:request')


def test_find_request_doesnt_exist(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    with pytest.raises(RequestNotImplementsError):
        find_request('request')


def test_find_request_doesnt_exist_in_module(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {'module': {}})
    with pytest.raises(RequestNotImplementsError):
        find_request('module:request')


def test_find_request_duplicit_request_name(monkeypatch):
    req1 = mock_request(module='module1', name='request')
    req2 = mock_request(module='module2', name='request')
    requests = {
        req1.module: {req1.name: req1},
        req2.module: {req2.name: req2}
    }
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    with pytest.raises(AmbiguousRequestNameError):
        find_request('request')


def test_find_request_multiple_in_same_module(monkeypatch):
    req1 = mock_request(name='request1')
    req2 = mock_request(name='request2')
    requests = {
        req1.module: {
            req1.name: req1,
            req2.name: req2,
        },
    }
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request(req1.name) == req1
    assert find_request(req2.name) == req2


def test_register_request(monkeypatch, mocked_request):
    requests = {}
    monkeypatch.setattr(dbgr.requests, '_REQUESTS', requests)
    register_request(mocked_request)
    assert requests == {mocked_request.module: {mocked_request.name: mocked_request}}


def test_register_multiple_requests_same_module(monkeypatch):
    requests = {}
    monkeypatch.setattr(dbgr.requests, '_REQUESTS', requests)
    req1 = mock_request(name='request1', module='module')
    req2 = mock_request(name='request2', module='module')
    register_request(req1)
    register_request(req2)
    assert requests == {'module': {req1.name: req1, req2.name: req2}}


def test_register_multiple_requests_different_module(monkeypatch):
    requests = {}
    monkeypatch.setattr(dbgr.requests, '_REQUESTS', requests)
    req1 = mock_request(name='request', module='module1')
    req2 = mock_request(name='request', module='module2')
    register_request(req1)
    register_request(req2)
    assert requests == {
        req1.module: {req1.name: req1},
        req2.module: {req2.name: req2}
    }

@pytest.mark.parametrize('name, result', [
    ('module:request', ('module', 'request')),
    ('module', ('module', None)),
    (None, (None, None)),
    (':request', (None, 'request')),
])
def test_parse_module_name(name, result):
    assert parse_module_name(name) == result


@pytest.mark.parametrize('name, result', [
    ('module:request', ('module', 'request')),
    ('request', (None, 'request')),
    (None, (None, None)),
    (':request', (None, 'request')),
])
def test_parse_request_name(name, result):
    assert parse_request_name(name) == result


def test_load_module(monkeypatch):
    class mocked_spec:
        def __init__(self):
            self.loaded = []
            self.loader = type('', (), {})()
            self.loader.exec_module = self.exec_module

        def exec_module(self, module):
            self.loaded.append(module)

    loaded_spec = mocked_spec()

    def mocked_spec_from_file(name, path):
        assert name == 'module'
        assert path == '/path/module.py'
        return loaded_spec

    def mocked_module_from_spec(spec):
        assert spec == loaded_spec
        return 'loaded_module'


    monkeypatch.setattr(dbgr.requests.importlib.util, 'spec_from_file_location', mocked_spec_from_file)
    monkeypatch.setattr(dbgr.requests.importlib.util, 'module_from_spec', mocked_module_from_spec)
    load_module('/path/module.py')
    assert loaded_spec.loaded == ['loaded_module']


def test_load_modules(monkeypatch):
    loaded = []
    def mocked_load(module):
        loaded.append(module)
    monkeypatch.setattr(dbgr.requests.glob, 'glob', lambda _: ['/path1/module1.py', '/path2/module2.py'])
    monkeypatch.setattr(dbgr.requests, 'load_module', mocked_load)
    load_requests()
    assert loaded == ['/path1/module1.py', '/path2/module2.py']


@pytest.mark.asyncio
async def test_execute_request(monkeypatch, capsys, mocked_session, mocked_env):
    async def mocked_Request(environment, session, use_defaults, cache, kwargs):
        assert environment == mocked_env
        assert session == mocked_session
        assert use_defaults == True
        assert cache == 'session'
        assert kwargs == {'arg1': 'val1', 'arg2': 'val2'}
        return Result('result', PrimitiveType(str))

    monkeypatch.setattr(dbgr.requests, 'find_request', lambda _: mocked_Request)
    assert 'result' == await execute_request(
        'request', mocked_env, mocked_session, True, 'session', arg1='val1', arg2='val2'
    )
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == "Result (str):\n'result'\n"


def test_access_module_and_name():
    async def func():
        pass

    req = Request(func)
    assert req.name == 'func'
    assert req.module == __name__


def test_access_module_and_alternative_name():
    async def func():
        pass

    req = Request(func, 'alternative_name')
    assert req.name == 'alternative_name'
    assert req.module == __name__


def test_invalid_name():
    async def func(env, session):
        pass

    with pytest.raises(dbgr.requests.InvalidRequestNameError):
        Request(func, 'invalid name')


def test_duplicit_name(monkeypatch):
    monkeypatch.setattr(
        dbgr.requests, 'get_requests', lambda: {__name__: {'func': lambda: None}}
    )
    async def func(env, session):
        pass

    with pytest.raises(dbgr.requests.DuplicateRequestNameError):
        Request(func)


def test_get_doc():
    async def func(env, session):
        ''' Docstring '''
        pass

    assert Request(func).doc == 'Docstring'


def test_get_empty_docstring():
    async def func():
        pass

    assert Request(func).doc == ''


def test_get_extra_arguments():
    async def func(arg_1, arg_2: int, arg_3='def3', arg_4: str='def4'):
        pass

    extras = Request(func).extra_arguments
    assert len(extras) == 4

    arg_1 = extras[0]
    assert isinstance(arg_1, NoDefaultValueArgument)
    assert arg_1.name == 'arg_1'
    assert isinstance(arg_1.annotation, Type)

    arg_2 = extras[1]
    assert isinstance(arg_2, NoDefaultValueArgument)
    assert arg_2.name == 'arg_2'
    assert isinstance(arg_2.annotation, PrimitiveType)

    arg_3 = extras[2]
    assert isinstance(arg_3, DefaultValueArgument)
    assert arg_3.name == 'arg_3'
    assert arg_3.value == 'def3'
    assert isinstance(arg_3.annotation, Type)

    arg_4 = extras[3]
    assert isinstance(arg_4, DefaultValueArgument)
    assert arg_4.name == 'arg_4'
    assert arg_4.value == 'def4'
    assert isinstance(arg_4.annotation, Type)
    assert arg_4.annotation.cls == str


def test_resolve_arguments_passed_with_env_session(mocked_env, mocked_session):
    async def func(env, session, arg_1):
        pass

    args = Request(func).resolve_arguments(mocked_env, mocked_session, False, {'arg_1': 123})
    assert args == {'arg_1': 123, 'env': mocked_env, 'session': mocked_session}


def test_resolve_arguments_passed_with_env(mocked_env, mocked_session):
    async def func(env, arg_1):
        pass

    args = Request(func).resolve_arguments(mocked_env, mocked_session, False, {'arg_1': 123})
    assert args == {'arg_1': 123, 'env': mocked_env}


def test_resolve_arguments_passed_with_session(mocked_env, mocked_session):
    async def func(session, arg_1):
        pass

    args = Request(func).resolve_arguments(mocked_env, mocked_session, False, {'arg_1': 123})
    assert args == {'arg_1': 123, 'session': mocked_session}


def test_resolve_arguments_passed(mocked_env, mocked_session):
    async def func(arg_1):
        pass

    args = Request(func).resolve_arguments(mocked_env, mocked_session, False, {'arg_1': 123})
    assert args == {'arg_1': 123}


def test_resolve_arguments_empty(mocked_env, mocked_session):
    async def func():
        pass

    args = Request(func).resolve_arguments(mocked_env, mocked_session, False, {'arg_1': 123})
    assert args == {}


def test_resolve_arguments_use_default(mocked_env, mocked_session):
    async def func(arg_1='default'):
        pass

    args = Request(func).resolve_arguments(mocked_env, mocked_session, True, {})
    assert args == {'arg_1': 'default'}


def test_resolve_arguments_defaults_dont_overwrite_passed(mocked_env, mocked_session):
    async def func(arg_1='default'):
        pass

    args = Request(func).resolve_arguments(mocked_env, mocked_session, True, {'arg_1': 'passed'})
    assert args == {'arg_1': 'passed'}


def test_prompts_for_missing_values(monkeypatch, mocked_env, mocked_session):
    monkeypatch.setattr(NoDefaultValueArgument, 'get_value', lambda *_, **__: 'input')
    async def func(arg_1):
        pass

    req = Request(func)
    args = req.resolve_arguments(mocked_env, mocked_session, False, {})
    assert args == {'arg_1': 'input'}


def test_format_bare(mocked_request):
    assert escape_ansi(mocked_request) == f'- {mocked_request.name}\n'


def test_format_bare_pydoc():
    async def func(env, session):
        ''' Pydoc '''
        pass
    assert escape_ansi(Request(func)) == '- func\n  Pydoc\n'


def test_format_arguments():
    async def func(arg_1, arg_2: int, arg_3: int=3, arg_4=4):
        pass
    assert escape_ansi(Request(func)) == (
        '- func\n'
        '  Arguments:\n'
        '   - arg_1\n'
        '   - arg_2 [type: int]\n'
        '   - arg_3 [default: 3, type: int]\n'
        '   - arg_4 [default: 4]\n'
    )


def test_format_arguments_with_session_and_env():
    async def func(env, session, arg_1, arg_2: int, arg_3: int=3, arg_4=4):
        pass
    assert escape_ansi(Request(func)) == (
        '- func\n'
        '  Arguments:\n'
        '   - arg_1\n'
        '   - arg_2 [type: int]\n'
        '   - arg_3 [default: 3, type: int]\n'
        '   - arg_4 [default: 4]\n'
    )


def test_format_cached():
    async def func(env, session):
        ''' Pydoc '''
        pass

    req = Request(func, cache='session')
    assert escape_ansi(req) == (
        '- func\n'
        '  [cache: session]\n'
        '  Pydoc\n'
    )


def test_format_typed():
    async def func(env, session) -> int:
        ''' Pydoc '''
        pass

    req = Request(func)
    assert escape_ansi(req) == (
        '- func\n'
        '  [return: int]\n'
        '  Pydoc\n'
    )

def test_format_cached_and_typed():
    async def func(env, session) -> int:
        ''' Pydoc '''
        pass

    req = Request(func, cache='session')
    assert escape_ansi(req) == (
        '- func\n'
        '  [cache: session, return: int]\n'
        '  Pydoc\n'
    )


@pytest.mark.asyncio
async def test_bare_call(mocked_env, mocked_session):
    req = mock_request(result='result')
    res = await req(mocked_env, mocked_session)
    assert  res.value == 'result'


@pytest.mark.asyncio
async def test_call_passes_arguments(mocked_env, mocked_session):
    async def func(arg):
        return arg

    req = Request(func)
    res = await req(mocked_env, mocked_session, kwargs={'arg': 'value'})
    assert  res.value == 'value'


@pytest.mark.asyncio
async def test_call_passes_arguments_env_session(mocked_env, mocked_session):
    async def func(env, session, arg):
        assert env == mocked_env
        assert session == mocked_session
        return arg

    req = Request(func)
    res = await req(mocked_env, mocked_session, kwargs={'arg': 'value'})
    assert  res.value == 'value'


@pytest.mark.asyncio
async def test_call_passes_arguments_session_env(mocked_env, mocked_session):
    async def func(session, env, arg):
        assert env == mocked_env
        assert session == mocked_session
        return arg

    req = Request(func)
    res = await req(mocked_env, mocked_session, kwargs={'arg': 'value'})
    assert  res.value == 'value'


@pytest.mark.asyncio
async def test_call_resolves_defaults(mocked_env, mocked_session):
    async def func(arg='default'):
        return arg

    req = Request(func)
    res = await req(mocked_env, mocked_session, use_defaults=True)
    assert  res.value == 'default'


@pytest.mark.asyncio
async def test_cached_request_first_call_not_cached(mocked_env, mocked_session):
    async def func():
        return 'value'

    req = Request(func, cache='session')
    res = await req(mocked_env, mocked_session)
    assert res.value == 'value'
    assert res.cached == False

@pytest.mark.asyncio
async def test_cached_request_first_call_not_cached_with_env(mocked_env, mocked_session):
    async def func(env):
        return 'value'

    req = Request(func, cache='session')
    res = await req(mocked_env, mocked_session)
    assert res.value == 'value'
    assert res.cached == False


@pytest.mark.asyncio
async def test_cached_request_second_call_cached(mocked_env, mocked_session):
    async def func():
        func.counter += 1
        return 'value'
    func.counter = 0

    req = Request(func, cache='session')
    await req(mocked_env, mocked_session)
    res = await req(mocked_env, mocked_session)
    assert res.value == 'value'
    assert res.cached == True
    assert func.counter == 1


@pytest.mark.asyncio
async def test_argument_is_part_of_cache_key(mocked_env, mocked_session):
    async def func(arg):
        return arg

    req = Request(func, cache='session')
    res_1 = await req(mocked_env, mocked_session, kwargs={'arg': 1})
    assert res_1.value == 1
    assert res_1.cached == False

    res_2 = await req(mocked_env, mocked_session, kwargs={'arg': 2})
    assert res_2.value == 2
    assert res_2.cached == False


def test_request_decorator_no_params():
    async def req_function():
        pass

    req = request_decorator(req_function)
    assert isinstance(req, Request)
    assert req.request == req_function
    assert req.cache == None
    assert req.name == 'req_function'


def test_request_decorator_with_cache():
    async def req_function():
        pass

    req = request_decorator(cache='session')(req_function)
    assert isinstance(req, Request)
    assert req.request == req_function
    assert req.cache == 'session'
    assert req.name == 'req_function'


def test_request_decorator_with_name():
    async def req_function():
        pass

    req = request_decorator(name='alternative_name')(req_function)
    assert isinstance(req, Request)
    assert req.request == req_function
    assert req.cache == None
    assert req.name == 'alternative_name'


def test_request_decorator_with_name_and_cache():
    async def req_function():
        pass

    req = request_decorator(cache='session', name='alternative_name')(req_function)
    assert isinstance(req, Request)
    assert req.request == req_function
    assert req.cache == 'session'
    assert req.name == 'alternative_name'
