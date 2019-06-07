from dbgr.reporting import Reporter
import pytest
from tests.conftest import MockedResponse, Params, escape_ansi


@pytest.mark.asyncio
async def test_resporter_print_request(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        data='OK',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, Params(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
< 200 OK
<
< Headers:
<  Content-Type: text/plain
<
< Content (text/plain):
OK
'''


@pytest.mark.asyncio
async def test_resporter_print_error_request(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        data='error',
        url='http://example.com',
        status=500
    )
    await Reporter().report_request_finished(mocked_session, {}, Params(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
< 500 Internal Server Error
<
< Headers:
<  Content-Type: text/plain
<
< Content (text/plain):
error
'''


@pytest.mark.asyncio
async def test_resporter_print_request_json(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'application/json'},
        data='{"key": "value"}',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, Params(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
< 200 OK
<
< Headers:
<  Content-Type: application/json
<
< Content (application/json):
{
  "key": "value"
}

'''


@pytest.mark.asyncio
async def test_resporter_print_request_xml(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'application/xml'},
        data='<tag>value</tag>',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, Params(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
< 200 OK
<
< Headers:
<  Content-Type: application/xml
<
< Content (application/xml):
<tag>value</tag>

'''


@pytest.mark.asyncio
async def test_resporter_print_request_xml(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'binary'},
        data=b'binary',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, Params(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
< 200 OK
<
< Headers:
<  Content-Type: binary
<
< Content (binary):
'''
