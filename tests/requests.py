import random
import pytest
import dbgr.requests
from dbgr.requests import (
    parse_cmd_arguments, get_requests, extract_module_name, Request, find_request,
    RequestNotImplementsError, AmbiguousRequestNameError, register_request
)


def _mocked_request(name, module=None):
    async def test_request():
        pass
    if module:
        test_request.__module__ = module
    return Request(test_request, name=name)


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


@pytest.mark.parametrize('path, name', [
    ('some/path/module.py', 'module'),
    ('../../relative/path.py', 'path'),
    ('simple.py', 'simple'),
    ('with-special_characters.py', 'with-special_characters')
])
def test_extract_module_name(path, name):
    assert extract_module_name(path) == name




def test_find_request_by_name(monkeypatch):
    req = _mocked_request('request')
    requests = {'module': {'request': req}}
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request('request') == req


def test_find_request_by_module_and_name(monkeypatch):
    req = _mocked_request('request')
    requests = {'module': {'request': req}}
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request('module:request') == req


def test_find_request_by_module_and_duplicit_name(monkeypatch):
    req1 = _mocked_request('request')
    req2 = _mocked_request('request')
    requests = {
        'module1': {'request': req1 },
        'module2': {'request': req2}
    }
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request('module1:request') == req1


def test_find_request_module_doesnt_exist(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    with pytest.raises(RequestNotImplementsError):
        find_request('module:request')


def test_find_request_doesnt_exist(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
    with pytest.raises(RequestNotImplementsError):
        find_request('request')


def test_find_request_doesnt_exist_in_module(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {'module': {}})
    with pytest.raises(RequestNotImplementsError):
        find_request('module:request')


def test_find_request_duplicit_request_name(monkeypatch):
    req1 = _mocked_request('request')
    req2 = _mocked_request('request')
    requests = {
        'module1': {'request': req1},
        'module2': {'request': req2}
    }
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    with pytest.raises(AmbiguousRequestNameError):
        find_request('request') == req1


def test_find_request_multiple_adepts(monkeypatch):
    req1 = _mocked_request('request1')
    req2 = _mocked_request('request2')
    requests = {
        'module1': {
            'request': req1,
            'request2': req2
        },
    }
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: requests)
    assert find_request('request1') == req1


def test_register_request(monkeypatch):
    requests = {}
    monkeypatch.setattr(dbgr.requests, '_REQUESTS', requests)
    req = _mocked_request('request', module='module')
    register_request(req)
    assert requests == {'module': {'request': req}}


def test_register_multiple_requests_same_module(monkeypatch):
    requests = {}
    monkeypatch.setattr(dbgr.requests, '_REQUESTS', requests)
    req1 = _mocked_request('request1', module='module')
    req2 = _mocked_request('request2', module='module')
    register_request(req1)
    register_request(req2)
    assert requests == {'module': {'request1': req1, 'request2': req2}}


def test_register_multiple_requests_different_module(monkeypatch):
    requests = {}
    monkeypatch.setattr(dbgr.requests, '_requests', requests)
    req1 = _mocked_request('request', module='module1')
    req2 = _mocked_request('request', module='module2')
    register_request(req1)
    register_request(req2)
    assert requests == {
        'module1': {'request': req1},
        'module2': {'request': req2}
    }
