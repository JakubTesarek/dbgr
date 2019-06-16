from dbgr.reporting import Reporter, ProgressBar
import pytest
from tests.conftest import MockedResponse, AiohttpParams, escape_ansi, MockedTraceContext
import asyncio
import re
import aiohttp
import os


@pytest.mark.asyncio
async def test_reporter_print_request(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        data='OK',
        url='http://example.com'
    )
    ctx = MockedTraceContext()
    await Reporter().on_request_end(mocked_session, ctx,  AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
<
< Response headers:
<  Content-Type: text/plain
<
< Response data (text/plain):
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
    ctx = MockedTraceContext()
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    print(captured.out)
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 500 Internal Server Error
>
> Request headers:
<
< Response headers:
<  Content-Type: text/plain
<
< Response data (text/plain):
error
'''


@pytest.mark.asyncio
async def test_reporter_print_response_json(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'application/json'},
        data='{"key": "value"}',
        url='http://example.com'
    )
    ctx = MockedTraceContext()
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
<
< Response headers:
<  Content-Type: application/json
<
< Response data (application/json):
{
  "key": "value"
}
'''

@pytest.mark.asyncio
async def test_reporter_print_response_html(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/html'},
        data='<html><body><h1>Hello world!</h1></body></html>',
        url='http://example.com'
    )
    ctx = MockedTraceContext()
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
<
< Response headers:
<  Content-Type: text/html
<
< Response data (text/html):
<html><body><h1>Hello world!</h1></body></html>
'''

@pytest.mark.asyncio
async def test_reporter_print_response_xml(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'application/xml'},
        data='<tag>value</tag>',
        url='http://example.com'
    )
    ctx = MockedTraceContext()
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
<
< Response headers:
<  Content-Type: application/xml
<
< Response data (application/xml):
<tag>value</tag>
'''


@pytest.mark.asyncio
async def test_reporter_print_response_binary(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'binary'},
        data=b'binary',
        url='http://example.com'
    )
    ctx = MockedTraceContext()
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
<
< Response headers:
<  Content-Type: binary
<
< Response data (binary):
b'binary'
'''


@pytest.mark.asyncio
async def test_progress_bar(capsys, mocked_session):
    par = AiohttpParams(MockedResponse())
    rep = ProgressBar()
    ctx = MockedTraceContext()
    await rep.on_request_start(mocked_session, ctx, par)
    await asyncio.sleep(0.5)
    output = escape_ansi(capsys.readouterr().out).strip()
    await rep.on_request_end(mocked_session, ctx, par)
    for line in output.splitlines():
        assert re.match(r'^request send . \[0:00:00\.\d{6}\]$', line)


@pytest.mark.asyncio
async def test_progress_bar_stop(mocked_session):
    par = AiohttpParams(MockedResponse())
    rep = ProgressBar()
    ctx = MockedTraceContext()
    await rep.on_request_start(mocked_session, ctx, par)
    await rep.on_request_end(mocked_session, ctx, par)
    await asyncio.sleep(0.2)


@pytest.mark.asyncio
async def test_progress_bar_redirect(capsys, mocked_session):
    par = AiohttpParams(MockedResponse(), url='example.com')
    rep = ProgressBar()
    await rep.on_request_start(mocked_session, {}, par)
    await rep.on_request_redirect(mocked_session, {}, par)
    await asyncio.sleep(0.2)
    output = escape_ansi(capsys.readouterr().out).strip()
    await rep.on_request_end(mocked_session, {}, par)
    for line in output.splitlines():
        assert re.match(r'^(request send|redirecting) . \[0:00:00\.\d{6}\]$', line)


@pytest.mark.asyncio
async def test_reporter_print_request_headers(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        url='http://example.com',
        request={'headers': {
            'key': 'value',
            'Content-Type': 'text/plain'
        }}
    )
    ctx = MockedTraceContext()
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
>  key: value
>  Content-Type: text/plain
<
< Response headers:
<  Content-Type: text/plain
<
< Response data (text/plain):

'''


@pytest.mark.asyncio
async def test_reporter_print_request_json(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        url='http://example.com',
        request={'headers': {'Content-Type': 'application/json'}}
    )
    ctx = MockedTraceContext(json = {'key': 'value'})
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
>  Content-Type: application/json
>
> Request data (application/json):
{
  "key": "value"
}
<
< Response headers:
<  Content-Type: text/plain
<
< Response data (text/plain):

'''


@pytest.mark.asyncio
async def test_reporter_print_request_binary(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        url='http://example.com',
        request={'headers':{'Content-Type': 'application/octet-stream'}}
    )
    ctx = MockedTraceContext(data=b'binary data')
    await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''> GET http://example.com
> 200 OK
>
> Request headers:
>  Content-Type: application/octet-stream
>
> Request data (application/octet-stream):
b'binary data'
<
< Response headers:
<  Content-Type: text/plain
<
< Response data (text/plain):

'''


@pytest.mark.asyncio
async def test_reporter_print_request_multipart(capsys, mocked_session):
    res = MockedResponse(
        headers={'Content-Type': 'text/plain'},
        url='http://example.com',
        request={'headers':{'Content-Type': 'multipart/form-data'}}
    )
    with aiohttp.MultipartWriter('form-data') as mpwriter:
        mpwriter.append_json({
                'breed': 'quick_expense',
                'date': '2019-04-16',
                'amount': 0,
                'currency': 'STD',
                'expense_type': 'OTHER'
            },
            headers={
                'content-disposition': 'form-data;name=metadata',
                'content-type': 'application/json'
            }
        )
        mpwriter.append(b'this is not a jpeg', headers={
            'content-type': 'image/jpeg',
            'content-disposition': 'form-data;name=receipt'
        })
        mpwriter.append(open(__file__, 'rb'))
        ctx = MockedTraceContext(data=mpwriter)
        await Reporter().on_request_end(mocked_session, ctx, AiohttpParams(res))
        captured = capsys.readouterr()
        assert escape_ansi(captured.out) == f'''> GET http://example.com
> 200 OK
>
> Request headers:
>  Content-Type: multipart/form-data
>
> Request data (multipart/form-data):
>  metadata (application/json):
>  - Encoding: utf-8
>  - Size: 105B
>  - Headers:
>     content-type: application/json
>     content-disposition: form-data;name=metadata
>     Content-Length: 105
>  - Content:
{{
  "amount": 0,
  "breed": "quick_expense",
  "currency": "STD",
  "date": "2019-04-16",
  "expense_type": "OTHER"
}}
>  receipt (image/jpeg):
>  - Size: 18B
>  - Headers:
>     content-type: image/jpeg
>     content-disposition: form-data;name=receipt
>     Content-Length: 18
>  - Content:
b'this is not a jpeg'
>  # Part (text/x-python):
>  - Filename: reporting.py
>  - Size: {os.path.getsize(__file__)}B
>  - Headers:
>     Content-Type: text/x-python
>     Content-Disposition: attachment; filename="{os.path.basename(__file__)}"; filename*=utf-8''{os.path.basename(__file__)}
>     Content-Length: {os.path.getsize(__file__)}
>  - Content:
Contents of "{__file__}"
<
< Response headers:
<  Content-Type: text/plain
<
< Response data (text/plain):

'''
