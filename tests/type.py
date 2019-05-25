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
    assert bool(t) == False


@pytest.mark.parametrize('cls, value_in, value_out', [
        (str, False, 'False'),
        (str, 'str', 'str'),
        (str, 1, '1'),
        (str, .1, '0.1'),
        (int, False, 0),
        (int, True, 1),
        (int, '1', 1),
        (int, 1, 1),
        (int, 1.9, 1),
        (float, False, 0.0),
        (float, True, 1),
        (float, '1', 1.0),
        (float, '1.0', 1),
        (float, 1.0, 1.0)
    ])
def test_cast_values(cls, value_in, value_out):
    t = Type(cls)
    assert t.cast(value_in) == value_out


@pytest.mark.parametrize('cls', [bool, str, int, float])
def test_none_is_cast_to_none(cls):
    t = Type(cls)
    assert t.cast(None) is None


@pytest.mark.parametrize('value', [1, 1.0, [], 'string', False, object()])
def testing_casting_to_invalid_type_passes_value_unchanged(value):
    t = Type(object)
    assert t.cast(value) == value


@pytest.mark.parametrize('value', [0, 'f', 'NO', 'False', 'n', False])
def test_cast_boolean_false(value):
    t = Type(bool)
    assert t.cast(value) == False

