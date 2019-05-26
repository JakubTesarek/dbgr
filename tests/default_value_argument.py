from dbgr.requests import DefaultValueArgument, Type
from tests.conftest import escape_ansi

def test_returns_given_value():
    a = DefaultValueArgument('name', Type(None), 'default')
    assert a.get_value({'name': 3.14}) == 3.14


def test_cast_value():
    a = DefaultValueArgument('name', Type(int), 'default')
    assert a.get_value({'name': 3.14}) == 3


def test_without_type_to_string():
    a = DefaultValueArgument('name', Type(None), 3.14)
    assert str(a) == 'name [default: 3.14]'


def test_with_type_to_string():
    a = DefaultValueArgument('name', Type(int), 2)
    assert str(a) == 'name [default: 2, type: int]'


def test_prompts_for_value(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'string')
    a = DefaultValueArgument('name', Type(str), 'default')
    assert a.get_value({}) == 'string'


def test_empty_input_returns_default(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '')
    a = DefaultValueArgument('name', Type(str), 'default')
    assert a.get_value({}) == 'default'


def test_force_usage_of_default():
    a = DefaultValueArgument('name', Type(str), 'default')
    assert a.get_value({}, use_default=True) == 'default'


def test_passed_arguement_rewrites_default():
    a = DefaultValueArgument('name', Type(str), 'default')
    assert a.get_value({'name': 'value'}, use_default=True) == 'value'


def test_prompts_until_correct_type_given(monkeypatch, capsys):
    inputs = ['invalid', '2']
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    a = DefaultValueArgument('name', Type(int), 'default')
    assert a.get_value({}) == 2
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == 'String "invalid" cannot be converted to int\n'
