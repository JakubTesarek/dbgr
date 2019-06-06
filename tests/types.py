import pytest
from dbgr.types import (
    Type, SecretType, PrimitiveType, BooleanType, DatetimeType, TimeType,
    DateType
)
from datetime import datetime, time, date
from dbgr import types
import dateparser


@pytest.mark.parametrize('cls', [str, int, float])
def test_create_primitive_type(cls):
    t = Type.get_type(cls)
    assert isinstance(t, PrimitiveType)
    assert str(t) == cls.__name__
    assert bool(t) == True


def test_create_boolean_typ():
    t = Type.get_type(bool)
    assert isinstance(t, BooleanType)
    assert str(t) == 'bool'
    assert bool(t) == True


def test_create_time_type():
    t = Type.get_type(time)
    assert isinstance(t, TimeType)
    assert str(t) == 'time'
    assert bool(t) == True


def test_create_date_type():
    t = Type.get_type(date)
    assert isinstance(t, DateType)
    assert str(t) == 'date'
    assert bool(t) == True


def test_create_datetime_type():
    t = Type.get_type(datetime)
    assert isinstance(t, DatetimeType)
    assert str(t) == 'datetime'
    assert bool(t) == True


@pytest.mark.parametrize('cls', [None, dict, list, tuple, object])
def test_create_unsupported_type(cls):
    t = Type.get_type(cls)
    assert isinstance(t, Type)
    assert str(t) == ''
    assert bool(t) == False


@pytest.mark.parametrize('cls', [None, dict, list, tuple, object])
def test_create_unsupported_primitive_type(cls):
    with pytest.raises(TypeError):
        PrimitiveType(cls)


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
    t = PrimitiveType(cls)
    assert t.cast(value_in) == value_out


@pytest.mark.parametrize('cls', [str, int, float])
def test_none_is_cast_to_none(cls):
    t = PrimitiveType(cls)
    assert t.cast(None) is None



@pytest.mark.parametrize('value', [1, 1.0, [], 'string', False, object()])
def testing_casting_to_invalid_type_passes_value_unchanged(value):
    t = Type.get_type(object)
    assert t.cast(value) == value


@pytest.mark.parametrize('value', [0, 'f', 'NO', 'False', 'n', False, [], {}])
def test_cast_boolean_false(value):
    t = BooleanType()
    assert t.cast(value) == False


@pytest.mark.parametrize('value', [1, 't', 'YES', 'True', 'y', True])
def test_cast_boolean_true(value):
    t = BooleanType()
    assert t.cast(value) == True


def test_cannot_cast_strings_to_int():
    t = PrimitiveType(int)
    with pytest.raises(ValueError):
        assert t.cast('string')


def test_cannot_cast_float_like_strings_to_int():
    t = PrimitiveType(int)
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
    t = PrimitiveType(cls)
    assert t.repr_value(value_in) == value_out


@pytest.mark.parametrize('value_in, value_out', [
    ('secret', 's****t'),
    ('short', '*****'),
    ('tiny', '****')
])
def test_value_representation(value_in, value_out):
    t = SecretType()
    assert t.repr_value(value_in) == value_out


@pytest.mark.parametrize('date_string', [
    ('2018-05-24'),
    ('today'),
    ('in 1 hour'),
    ('yesterday'),
    ('tomorrow'),
    ('midnight'),
    ('5 minutes ago'),
    ('in 3 hours')
])
def test_datetime_parser_parse_string_date(date_string):
    t = DatetimeType()
    assert isinstance(t.cast(date_string), datetime)


@pytest.mark.parametrize('date_string', [
    ('2018-05-24'),
    ('today'),
    ('in 1 hour'),
    ('yesterday'),
    ('tomorrow'),
    ('midnight'),
    ('5 minutes ago'),
    ('in 3 hours')
])
def test_date_parser_parse_string_date(date_string):
    t = DateType()
    assert isinstance(t.cast(date_string), date)


@pytest.mark.parametrize('date_string', [
    ('2018-05-24'),
    ('today'),
    ('in 1 hour'),
    ('yesterday'),
    ('tomorrow'),
    ('midnight'),
    ('5 minutes ago'),
    ('in 3 hours')
])
def test_date_parser_parse_string_date(date_string):
    t = TimeType()
    assert isinstance(t.cast(date_string), time)


@pytest.mark.parametrize('t', [
    DateType(), DatetimeType(), TimeType()
])
def test_date_parser_invalid_date_string(t):
    with pytest.raises(ValueError):
        t.cast('xxxxxxxxxx')


@pytest.mark.parametrize('date_object', [
    datetime.now(),
    datetime.now().time(),
    datetime.now().date(),
])
def test_date_parser_fills_in_missing_parts(date_object):
    t = DateType()
    assert isinstance(t.cast(date_object), date)


@pytest.mark.parametrize('date_object', [
    datetime.now(),
    datetime.now().time(),
    datetime.now().date(),
])
def test_datetime_parser_fills_in_missing_parts(date_object):
    t = DatetimeType()
    assert isinstance(t.cast(date_object), datetime)


@pytest.mark.parametrize('date_object', [
    datetime.now(),
    datetime.now().time(),
    datetime.now().date(),
])
def test_time_parser_fills_in_missing_parts(date_object):
    t = TimeType()
    assert isinstance(t.cast(date_object), time)


@pytest.mark.parametrize('t', [DateType(), DatetimeType(), TimeType()])
def test_date_parser_cast_none(t):
    assert t.cast(None) == None


def test_datetime_repr_string():
    t = DatetimeType()
    assert t.repr_value('2019-03-21 12:13:14.132120') == '2019-03-21 12:13:14.132120 (2019-03-21 12:13:14.132120)'


def test_date_repr_string():
    t = DateType()
    assert t.repr_value('2019-03-21 12:13:14.132120') == '2019-03-21 12:13:14.132120 (2019-03-21)'


def test_time_repr_string():
    t = TimeType()
    assert t.repr_value('2019-03-21 12:13:14.132120') == '2019-03-21 12:13:14.132120 (12:13:14.132120)'


def test_datetime_repr_datetime():
    t = DatetimeType()
    assert t.repr_value(datetime(2019, 3, 21, 12, 13, 14, 132120)) == '2019-03-21 12:13:14.132120'


def test_date_repr_datetime():
    t = DateType()
    assert t.repr_value(datetime(2019, 3, 21, 12, 13, 14, 132120)) == '2019-03-21'


def test_time_repr_datetime():
    t = TimeType()
    assert t.repr_value(datetime(2019, 3, 21, 12, 13, 14, 132120)) == '12:13:14.132120'

