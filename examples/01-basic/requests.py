from dbgr import request

@request
async def slow_response(env, session):
    await session.get(f'{env["DEFAULT"]["slow_url"]}/delay/1000/url/{env["DEFAULT"]["slow_url"]}/delay/3000/url/http://google.com')


@request
async def google(env, session):
    await session.get(f'http://google.com')
