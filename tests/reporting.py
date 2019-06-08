from dbgr.reporting import Reporter, ProgressBar
import pytest
from tests.conftest import MockedResponse, AiohttpParams, escape_ansi
import asyncio
import re


@pytest.mark.asyncio
async def test_reporter_print_request(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        data='OK',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, AiohttpParams(res))
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
async def test_reporter_print_error_request(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        data='error',
        url='http://example.com',
        status=500
    )
    await Reporter().report_request_finished(mocked_session, {}, AiohttpParams(res))
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
async def test_reporter_print_request_json(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'application/json'},
        data='{"key": "value"}',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, AiohttpParams(res))
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
async def test_reporter_print_request_xml(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'application/xml'},
        data='<tag>value</tag>',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, AiohttpParams(res))
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
async def test_reporter_print_request_binary(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'binary'},
        data=b'binary',
        url='http://example.com'
    )
    await Reporter().report_request_finished(mocked_session, {}, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
< 200 OK
<
< Headers:
<  Content-Type: binary
<
< Content (binary):
'''


@pytest.mark.asyncio
async def test_reporter_print_redirect(capsys, mocked_session):
    res = MockedResponse()
    par = AiohttpParams(res, url='http://example.com')
    await Reporter().on_request_redirect(mocked_session, {}, par)
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == 'Redirect -> http://example.com\n'


@pytest.mark.asyncio
async def test_progress_bar(capsys, mocked_session):
    par = AiohttpParams(MockedResponse())
    rep = ProgressBar()
    await rep.on_request_start(mocked_session, {}, par)
    await asyncio.sleep(0.5)
    output = escape_ansi(capsys.readouterr().out)
    await rep.on_request_end(mocked_session, {}, par)
    for line in output.splitlines():
        assert re.match(r'^request send . \[0:00:00\.\d{6}\]$', line)


@pytest.mark.asyncio
async def test_progress_bar_stop(mocked_session):
    par = AiohttpParams(MockedResponse())
    rep = ProgressBar()
    await rep.on_request_start(mocked_session, {}, par)
    await rep.on_request_end(mocked_session, {}, par)
    await asyncio.sleep(0.2)


@pytest.mark.asyncio
async def test_progress_bar_redirect(capsys, mocked_session):
    par = AiohttpParams(MockedResponse(), url='example.com')
    rep = ProgressBar()
    await rep.on_request_start(mocked_session, {}, par)
    await rep.on_request_redirect(mocked_session, {}, par)
    await asyncio.sleep(0.2)
    output = escape_ansi(capsys.readouterr().out)
    await rep.on_request_end(mocked_session, {}, par)
    for line in output.splitlines():
        assert re.match(r'^(request send|redirecting) . \[0:00:00\.\d{6}\]$', line)
