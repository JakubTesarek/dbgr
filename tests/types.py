import pytest
from dbgr.types import Type, SecretType


@pytest.mark.parametrize('cls', [bool, str, int, float])
def test_create_supported_type(cls):
    t = Type.get_type(cls)
    assert str(t) == cls.__name__
    assert bool(t) == True


@pytest.mark.parametrize('cls', [dict, list, tuple, object])
def test_create_unsupported_type(cls):
    t = Type.get_type(cls)
    assert str(t) == ''
    assert bool(t) == False


def test_create_sectet_type():
    t = Type.get_type(SecretType)
    assert str(t) == 'secret'
    assert bool(t) == True
    assert isinstance(t, SecretType)


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


def test_cannot_cast_strings_to_int():
    t = Type(int)
    with pytest.raises(ValueError):
        assert t.cast('string')


def test_cannot_cast_float_like_strings_to_int():
    t = Type(int)
    with pytest.raises(ValueError):
        assert t.cast('3.14')


@pytest.mark.parametrize('cls, value_in, value_out', [
    (str, False, 'False'),
    (str, 'str', 'str'),
    (str, 1, '1'),
    (str, .1, '0.1'),
    (int, False, '0'),
    (int, True, '1'),
    (int, '1', '1'),
    (int, 1, '1'),
    (int, 1.9, '1'),
    (float, False, '0.0'),
    (float, True, '1.0'),
    (float, '1', '1.0'),
    (float, 1.0, '1.0')
])
def test_value_representation(cls, value_in, value_out):
    t = Type(cls)
    assert t.repr_value(value_in) == value_out


@pytest.mark.parametrize('value_in, value_out', [
    ('secret', 's****t'),
    ('short', '*****'),
    ('tiny', '****')
])
def test_value_representation(value_in, value_out):
    t = SecretType()
    assert t.repr_value(value_in) == value_out
