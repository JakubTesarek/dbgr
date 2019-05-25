from dbgr.requests import NoDefaultValueArgument, Type

def test_returns_given_value():
    a = NoDefaultValueArgument('name', Type(None))
    assert a.get_value({'name': 3.14}) == 3.14


def test_cast_value():
    a = NoDefaultValueArgument('name', Type(int))
    assert a.get_value({'name': 3.14}) == 3


def test_without_type_to_string():
    a = NoDefaultValueArgument('name', Type(None))
    assert str(a) == 'name'


def test_with_type_to_string():
    a = NoDefaultValueArgument('name', Type(int))
    assert str(a) == 'name [type: int]'


def test_prompts_for_value(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'string')
    a = NoDefaultValueArgument('name', Type(str))
    assert a.get_value({}) == 'string'


def test_prompts_for_value_until_given(monkeypatch):
    inputs = ['', '', 'string']
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop())
    a = NoDefaultValueArgument('name', Type(str))
    assert a.get_value({}) == 'string'
