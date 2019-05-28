import pytest
import dbgr

@pytest.mark.asyncio
async def test_response_passes_kwargs(monkeypatch):
    async def mocked_execute_request(session, env, request, **kwargs):
        return kwargs
    monkeypatch.setattr(dbgr, 'execute_request', mocked_execute_request)
    res = await dbgr.response('request', None, None, arg_1='val1', arg_2='val2')
    assert res == {'arg_1': 'val1', 'arg_2': 'val2'}
