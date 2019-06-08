from dbgr import request

@request
async def slow_response(session, url='http://example.com', sleep_sec: int=3):
    await session.get(f'http://slowwly.robertomurray.co.uk/delay/{sleep_sec * 1000}/url/{url}')
