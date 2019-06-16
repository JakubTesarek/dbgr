import types
import pytest
import aiohttp
from dbgr import session


@pytest.mark.asyncio
async def test_get_session():
    sess = session.get_session()
    assert isinstance(sess, aiohttp.ClientSession)
    await sess.close()


@pytest.mark.asyncio
async def test_get_session_caches():
    sess1 = session.get_session()
    sess2 = session.get_session()
    assert sess1 == sess2
    await sess1.close()


@pytest.mark.asyncio
async def test_close_session():
    sess = session.get_session()
    assert not sess.closed
    await session.close_session()
    assert sess.closed


@pytest.mark.asyncio
async def test_close_session_no_session():
    assert session._SESSION == None
    await session.close_session()

@pytest.mark.asyncio
async def test_passes_request_params_to_request_context(monkeypatch):
    async def mocked__request(self, method, url, **kwargs):
        return kwargs['trace_request_ctx']

    monkeypatch.setattr(aiohttp.ClientSession, '_request', mocked__request)
    sess = session.get_session()
    ctx = await sess.get('url', headers={'key': 'value'}, timeout=42)
    assert ctx == types.SimpleNamespace(
        allow_redirects=True,
        headers={'key': 'value'},
        method='GET',
        timeout=42,
        url='url'
    )
