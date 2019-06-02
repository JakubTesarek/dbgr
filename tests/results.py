from dbgr.requests import Result, Type
from tests.conftest import escape_ansi


def test_returns_given_result():
    r = Result(3.14, Type(object))
    assert r.value == 3.14


def test_cast_value_if_possible():
    r = Result('3.14', Type(float))
    assert r.value == 3.14


def test_format_no_cache():
    r = Result('result', Type(None))
    assert escape_ansi(r) == 'Result (str):\n\'result\''


def test_format_cache():
    r = Result('result', Type(None), True)
    assert escape_ansi(r) == 'Result (str, from cache):\n\'result\''


def test_format_none():
    r = Result(None, Type(None), False)
    assert escape_ansi(r) == 'Result (NoneType)'
