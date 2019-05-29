'''
Api calls to REST testing server: http://jsonplaceholder.typicode.com
'''

from dbgr import request


@request
async def posts(env, session):
    ''' Retrieve all posts '''
    await session.get(f'{env["placeholder"]["url"]}/posts')
