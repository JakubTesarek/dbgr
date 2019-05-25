import pytest
from dbgr.requests import Type

@pytest.mark.parametrize('cls', [bool, str, int, float])
def test_create_supported_type(cls):
    t = Type(cls)
    assert str(t) == cls.__name__


@pytest.mark.parametrize('cls', [dict, list, tuple, object])
def test_create_unsupported_type(cls):
    t = Type(cls)
    assert str(t) == ''


@pytest.mark.parametrize('value', [0, 'f', 'NO', 'False', 'n', False])
def test_cast_boolean_false(value):
    t = Type(bool)
    assert t.cast(value) == False

