from dbgr.requests import DefaultValueArgument, NoDefaultValueArgument
from dbgr.types import PrimitiveType, Type, SecretType
from tests.conftest import escape_ansi

def test_default_value_argument_returns_given_value():
    a = DefaultValueArgument('name', Type(), 'default')
    assert a.get_value({'name': 3.14}) == 3.14


def test_default_value_argument_cast_value():
    a = DefaultValueArgument('name', PrimitiveType(int), 'default')
    assert a.get_value({'name': 3.14}) == 3


def test_default_value_argument_without_type_to_string():
    a = DefaultValueArgument('name', Type(), 3.14)
    assert str(a) == 'name [default: 3.14]'


def test_default_value_argument_with_type_to_string():
    a = DefaultValueArgument('name', PrimitiveType(int), 2)
    assert str(a) == 'name [default: 2, type: int]'


def test_default_value_argument_prompts_for_value(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'string')
    a = DefaultValueArgument('name', PrimitiveType(str), 'default')
    assert a.get_value({}) == 'string'


def test_default_value_argument_empty_input_returns_default(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '')
    a = DefaultValueArgument('name', PrimitiveType(str), 'default')
    assert a.get_value({}) == 'default'


def test_default_value_argument_force_usage_of_default():
    a = DefaultValueArgument('name', PrimitiveType(str), 'default')
    assert a.get_value({}, use_default=True) == 'default'


def test_default_value_argument_passed_arguement_rewrites_default():
    a = DefaultValueArgument('name', PrimitiveType(str), 'default')
    assert a.get_value({'name': 'value'}, use_default=True) == 'value'


def test_default_value_argument_prompts_until_correct_type_given(monkeypatch, capsys):
    inputs = ['invalid', '2']
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    a = DefaultValueArgument('name', PrimitiveType(int), '3')
    assert a.get_value({}) == 2
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == 'String "invalid" cannot be converted to int\n'


def test_default_value_argument_prompts_for_secret_value(monkeypatch, capsys):
    monkeypatch.setattr('getpass.getpass', lambda _: 'password')
    a = DefaultValueArgument('name', SecretType(), 'default')
    assert a.get_value({}) == 'password'


def test_default_value_argument_mistmatched_type_of_default_value():
    a = DefaultValueArgument('name', PrimitiveType(int), 'string')
    assert str(a) == 'name [default: string, type: int]'


def test_no_default_value_argument_returns_given_value():
    a = NoDefaultValueArgument('name', Type())
    assert a.get_value({'name': 3.14}) == 3.14


def test_no_default_value_argument_cast_value():
    a = NoDefaultValueArgument('name', PrimitiveType(int))
    assert a.get_value({'name': 3.14}) == 3


def test_no_default_value_argument_without_type_to_string():
    a = NoDefaultValueArgument('name', Type())
    assert str(a) == 'name'


def test_no_default_value_argument_with_type_to_string():
    a = NoDefaultValueArgument('name', PrimitiveType(int))
    assert str(a) == 'name [type: int]'


def test_no_default_value_argument_prompts_for_value(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'string')
    a = NoDefaultValueArgument('name', PrimitiveType(str))
    assert a.get_value({}) == 'string'


def test_no_default_value_argument_prompts_for_value_until_given(monkeypatch):
    inputs = ['', '', '2']
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    a = NoDefaultValueArgument('name', PrimitiveType(int))
    assert a.get_value({}) == 2
