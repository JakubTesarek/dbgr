import aiohttp
from dbgr import session


def test_get_session():
    assert isinstance(session.get_session(), aiohttp.ClientSession)
