from dbgr.requests import parse_cmd_arguments


def test_parse_cmd_arguments_empty():
    assert parse_cmd_arguments([]) == {}


def test_parse_cmd_arguments():
    args = ['arg1=val1', 'arg2=val2']
    assert parse_cmd_arguments(args) == {'arg1': 'val1', 'arg2': 'val2'}


def test_cmd_arguments_without_value_resolved_to_true():
    assert parse_cmd_arguments(['arg1']) == {'arg1': True}
