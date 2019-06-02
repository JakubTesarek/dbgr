import pytest
import aiohttp
from dbgr import session


@pytest.mark.asyncio
async def test_get_session():
    sess = session.get_session()
    assert isinstance(sess, aiohttp.ClientSession)
    await sess.close()
