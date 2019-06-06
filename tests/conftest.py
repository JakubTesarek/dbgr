import builtins
from io import StringIO
import re
import pytest
import dbgr.requests


def escape_ansi(string):
    return re.sub(r'\x1b[^m]*m', '', str(string))


real_open = builtins.open
@pytest.fixture
def mock_file(monkeypatch):
    def mock_file_fixture(filename, content):
        def mocked_open(filepath, **kwargs):
            if filename == filepath:
                return StringIO(content)
            return real_open(filepath, **kwargs)
        monkeypatch.setattr(builtins, 'open', mocked_open)
    return mock_file_fixture


def mock_request(name='request', module='module', result=None):
    async def test_request():
        return result
    if module:
        test_request.__module__ = module
    return dbgr.requests.Request(test_request, name=name)


def mock_request(name='request', module='module', result=None):
    async def test_request():
        return result
    if module:
        test_request.__module__ = module
    return dbgr.requests.Request(test_request, name=name)


@pytest.fixture
def mocked_request(name='request', module='module', result=None):
    async def test_request():
        return result
    if module:
        test_request.__module__ = module
    return dbgr.requests.Request(test_request, name=name)


class MockedAiohttpSession:
    def close(self):
        pass

    def __del__(self):
        pass


@pytest.fixture
def mocked_session():
    return MockedAiohttpSession()


@pytest.fixture
def mocked_env():
    return {}


@pytest.fixture(autouse=True)
def clear_cache():
    dbgr.requests._CACHE = {}
    yield
    dbgr.requests._CACHE = {}


@pytest.fixture(autouse=True)
def clear_environment():
    dbgr.environment._ENVIRONMENT = None
    yield
    dbgr.environment._ENVIRONMENT = None

@pytest.fixture(autouse=True)
def clear_session():
    dbgr.session._SESSION = None
    yield
    dbgr.session._SESSION = None


@pytest.fixture(autouse=True)
def mock_registered_requests(monkeypatch):
    monkeypatch.setattr(dbgr.requests, 'get_requests', lambda: {})
