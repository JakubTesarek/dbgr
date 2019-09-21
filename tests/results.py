from dbgr.results import Result
from dbgr.types import Type, PrimitiveType
from tests.conftest import escape_ansi


def test_returns_given_result():
    r = Result(3.14, Type())
    assert r.value == 3.14


def test_cast_value_if_possible():
    r = Result('3.14', PrimitiveType(float))
    assert r.value == 3.14


def test_format_none():
    r = Result(None, Type(), False)
    assert escape_ansi(r) == 'None'


def test_format_without_type():
    r = Result('string value')
    assert escape_ansi(r) == 'string value'
