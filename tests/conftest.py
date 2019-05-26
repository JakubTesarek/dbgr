import re
import pytest
import dbgr.requests

def escape_ansi(string):
    return re.sub(r'\x1b[^m]*m', '', str(string))


@pytest.fixture
def session():
    return object()


@pytest.fixture
def env():
    return {}


@pytest.fixture(autouse=True)
def clear_cache():
    dbgr.requests._CACHE = {}
    yield
    dbgr.requests._CACHE = {}


@pytest.fixture(autouse=True)
def mock_registered_requests(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
