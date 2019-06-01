import pytest
import dbgr.requests
from dbgr.requests import Request, DefaultValueArgument, NoDefaultValueArgument
from tests.conftest import escape_ansi


def test_access_module_and_name():
    async def func(env, session):
        pass

    req = Request(func)
    assert req.name == 'func'
    assert req.module == __name__


def test_access_module_and_alternative_name():
    async def func(env, session):
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
    async def func(env, session):
        pass

    assert Request(func).doc == ''


def test_get_extra_arguments():
    async def func(env, session, arg_1, arg_2: int, arg_3='def3', arg_4: str='def4'):
        pass

    extras = Request(func).extra_arguments
    assert len(extras) == 4

    arg_1 = extras[0]
    assert isinstance(arg_1, NoDefaultValueArgument)
    assert arg_1.name == 'arg_1'
    assert isinstance(arg_1.annotation, dbgr.requests.Type)
    assert arg_1.annotation.cls == None

    arg_2 = extras[1]
    assert isinstance(arg_2, NoDefaultValueArgument)
    assert arg_2.name == 'arg_2'
    assert isinstance(arg_2.annotation, dbgr.requests.Type)
    assert arg_2.annotation.cls == int

    arg_3 = extras[2]
    assert isinstance(arg_3, DefaultValueArgument)
    assert arg_3.name == 'arg_3'
    assert arg_3.value == 'def3'
    assert isinstance(arg_3.annotation, dbgr.requests.Type)
    assert arg_3.annotation.cls == None

    arg_4 = extras[3]
    assert isinstance(arg_4, DefaultValueArgument)
    assert arg_4.name == 'arg_4'
    assert arg_4.value == 'def4'
    assert isinstance(arg_4.annotation, dbgr.requests.Type)
    assert arg_4.annotation.cls == str


def test_resolve_arguments_passed_with_env_session():
    async def func(env, session, arg_1):
        pass

    args = Request(func).resolve_arguments('env', 'session', False, {'arg_1': 123})
    assert args == {'arg_1': 123, 'env': 'env', 'session': 'session'}


def test_resolve_arguments_passed_with_env():
    async def func(env, arg_1):
        pass

    args = Request(func).resolve_arguments('env', 'session', False, {'arg_1': 123})
    assert args == {'arg_1': 123, 'env': 'env'}


def test_resolve_arguments_passed_with_session():
    async def func(session, arg_1):
        pass

    args = Request(func).resolve_arguments('env', 'session', False, {'arg_1': 123})
    assert args == {'arg_1': 123, 'session': 'session'}


def test_resolve_arguments_passed():
    async def func(arg_1):
        pass

    args = Request(func).resolve_arguments('env', 'session', False, {'arg_1': 123})
    assert args == {'arg_1': 123}


def test_resolve_arguments_empty():
    async def func():
        pass

    args = Request(func).resolve_arguments('env', 'session', False, {'arg_1': 123})
    assert args == {}


def test_resolve_arguments_use_default():
    async def func(arg_1='default'):
        pass

    args = Request(func).resolve_arguments('env', 'session', True, {})
    assert args == {'arg_1': 'default'}


def test_resolve_arguments_defaults_dont_overwrite_passed():
    async def func(arg_1='default'):
        pass

    args = Request(func).resolve_arguments('env', 'session', True, {'arg_1': 'passed'})
    assert args == {'arg_1': 'passed'}


def test_prompts_for_missing_values(monkeypatch):
    monkeypatch.setattr(NoDefaultValueArgument, 'get_value', lambda *_, **__: 'input')
    async def func(arg_1):
        pass

    req = Request(func)
    args = req.resolve_arguments('env', 'session', False, {})
    assert args == {'arg_1': 'input'}


def test_format_bare():
    async def func(env, session):
        pass
    assert escape_ansi(Request(func)) == '- func\n'


def test_format_bare_pydoc():
    async def func(env, session):
        ''' Pydoc '''
        pass
    assert escape_ansi(Request(func)) == '- func\n  Pydoc\n'


def test_format_arguments():
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
async def test_bare_call(env, session):
    async def func(env, session):
        return 'result'
    req = Request(func)
    res = await req(env, session)
    assert  res.value == 'result'


@pytest.mark.asyncio
async def test_call_passes_arguments(env, session):
    async def func(env, session, arg):
        return arg

    req = Request(func)
    res = await req(env, session, kwargs={'arg': 'value'})
    assert  res.value == 'value'


@pytest.mark.asyncio
async def test_call_resolves_defaults(env, session):
    async def func(env, session, arg='default'):
        return arg

    req = Request(func)
    res = await req(env, session, use_defaults=True)
    assert  res.value == 'default'


@pytest.mark.asyncio
async def test_cached_request_first_call_not_cached(env, session):
    async def func(env, session):
        return 'value'

    req = Request(func, cache='session')
    res = await req(env, session)
    assert res.value == 'value'
    assert res.cached == False


@pytest.mark.asyncio
async def test_cached_request_second_call_cached(env, session):
    async def func(env, session):
        func.counter += 1
        return 'value'
    func.counter = 0

    req = Request(func, cache='session')
    await req(env, session)
    res = await req(env, session)
    assert res.value == 'value'
    assert res.cached == True
    assert func.counter == 1


@pytest.mark.asyncio
async def test_argument_is_part_of_cache_key(env, session):
    async def func(env, session, arg):
        return arg

    req = Request(func, cache='session')
    res_1 = await req(env, session, kwargs={'arg': 1})
    assert res_1.value == 1
    assert res_1.cached == False

    res_2 = await req(env, session, kwargs={'arg': 2})
    assert res_2.value == 2
    assert res_2.cached == False


