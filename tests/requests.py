import dbgr.requests
from dbgr.requests import parse_cmd_arguments, get_requests


def test_parse_cmd_arguments_empty():
    assert parse_cmd_arguments([]) == {}


def test_parse_cmd_arguments():
    args = ['arg1=val1', 'arg2=val2']
    assert parse_cmd_arguments(args) == {'arg1': 'val1', 'arg2': 'val2'}


def test_cmd_arguments_without_value_resolved_to_true():
    assert parse_cmd_arguments(['arg1']) == {'arg1': True}


def test_get_requests_loads_requests_once(monkeypatch):
    def mocked_load_requests():
        mocked_load_requests.counter += 1
        monkeypatch.setattr(dbgr.requests, '_REQUESTS', {'module': {}})
    mocked_load_requests.counter = 0
    monkeypatch.setattr(dbgr.requests, 'load_requests', mocked_load_requests)
    assert get_requests() == {'module': {}}
    assert get_requests() == {'module': {}}
    assert mocked_load_requests.counter == 1
