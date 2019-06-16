import types
import builtins
from io import StringIO
import re
import pytest
import dbgr.requests
import http.client
import aiohttp
from multidict import CIMultiDict
import pytest
import json


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


@pytest.fixture
def mocked_request():
    return mock_request()


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


class MockedResponse:
    def __init__(
            self, url='', method='GET', status=200, headers=None, data=None,
            request=None):
        request = {'headers': {}} if request is None else request
        request['headers'] = CIMultiDict(request['headers'])
        self.url = url
        self.method = method
        self.headers = CIMultiDict(headers if headers else {})
        self.status = status
        self.data = data
        self.request_info = types.SimpleNamespace(**request)

    @property
    def reason(self):
        return http.client.responses[self.status]

    async def text(self):
        return '' if self.data is None else self.data

    async def json(self):
        content_type = self.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            raise aiohttp.ContentTypeError()
        return json.loads(self.data)


class MockedTraceContext:
    def __init__(self, **kwargs):
        self.trace_request_ctx = types.SimpleNamespace(**kwargs)
    

class AiohttpParams:
    def __init__(self, response, url=''):
        self.response = response
        self.url = url


class attrdict:
    def __init__(self, d):
        self.__dict__ = d

