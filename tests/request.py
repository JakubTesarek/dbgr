import pytest
import dbgr.requests
from dbgr.requests import Request, DefaultValueArgument, NoDefaultValueArgument
from tests.conftest import escape_ansi


def test_access_module_and_name(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session):
        pass

    req = Request(func)
    assert req.name == 'func'
    assert req.module == __name__


def test_access_module_and_alternative_name(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session):
        pass

    req = Request(func, 'alternative_name')
    assert req.name == 'alternative_name'
    assert req.module == __name__


def test_invalid_name(monkeypatch):
    def func(env, session):
        pass

    with pytest.raises(dbgr.requests.InvalidRequestNameError):
        Request(func, 'invalid name')


def test_duplicit_name(monkeypatch):
    monkeypatch.setattr(
        dbgr.requests, 'get_requests', lambda: {__name__: {'func': lambda: None}}
    )
    def func(env, session):
        pass

    with pytest.raises(dbgr.requests.DuplicateRequestNameError):
        Request(func)


def test_get_doc(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session):
        ''' Docstring '''
        pass

    assert Request(func).doc == 'Docstring'


def test_get_empty_docstring(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session):
        pass

    assert Request(func).doc == ''


def test_get_extra_arguments(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session, arg_1, arg_2: int, arg_3='def3', arg_4: str='def4'):
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


def test_resolve_arguments_passed(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session, arg_1):
        pass

    args = Request(func).resolve_arguments(False, {'arg_1': 123})
    assert args == {'arg_1': 123}


def test_resolve_arguments_use_default(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session, arg_1='default'):
        pass

    args = Request(func).resolve_arguments(True, {})
    assert args == {'arg_1': 'default'}


def test_resolve_arguments_defaults_dont_overwrite_passed(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session, arg_1='default'):
        pass

    args = Request(func).resolve_arguments(True, {'arg_1': 'passed'})
    assert args == {'arg_1': 'passed'}


def test_prompts_for_missing_values(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    monkeypatch.setattr(NoDefaultValueArgument, 'get_value', lambda *_, **__: 'input')
    def func(env, session, arg_1):
        pass

    req = Request(func)
    args = req.resolve_arguments(False, {})
    assert args == {'arg_1': 'input'}


def test_format_bare(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session):
        pass
    assert escape_ansi(Request(func)) == '- func\n'


def test_format_bare_pydoc(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session):
        ''' Pydoc '''
        pass
    assert escape_ansi(Request(func)) == '- func\n  Pydoc\n'


def test_format_arguments(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session, arg_1, arg_2: int, arg_3: int=3, arg_4=4):
        pass
    assert escape_ansi(Request(func)) == (
        '- func\n'
        '  Arguments:\n'
        '   - arg_1\n'
        '   - arg_2 [type: int]\n'
        '   - arg_3 [default: 3, type: int]\n'
        '   - arg_4 [default: 4]\n'
    )


def test_format_cached(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session):
        ''' Pydoc '''
        pass
    req = Request(func, cache='session')
    assert escape_ansi(req) == (
        '- func\n'
        '  [cache: session]\n'
        '  Pydoc\n'
    )


def test_format_typed(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session) -> int:
        ''' Pydoc '''
        pass
    req = Request(func)
    assert escape_ansi(req) == (
        '- func\n'
        '  [return: int]\n'
        '  Pydoc\n'
    )

def test_format_cached_and_typed(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    def func(env, session) -> int:
        ''' Pydoc '''
        pass
    req = Request(func, cache='session')
    assert escape_ansi(req) == (
        '- func\n'
        '  [cache: session, return: int]\n'
        '  Pydoc\n'
    )
