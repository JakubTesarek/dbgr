from dbgr.requests import Result, Type


def test_returns_given_result():
    r = Result(3.14, Type(object))
    assert r.value == 3.14


def test_cast_value_if_possible():
    r = Result('3.14', Type(float))
    assert r.value == 3.14

