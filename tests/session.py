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
