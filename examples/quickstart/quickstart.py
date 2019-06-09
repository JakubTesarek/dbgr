'''
Quickstart example for  DBGR
'''

from dbgr import request


@request
async def get_example(session):
    ''' Retrieve example.com site'''
    await session.get('http://example.com')
