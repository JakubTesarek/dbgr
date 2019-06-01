'''
Api calls to REST testing server: http://jsonplaceholder.typicode.com
'''

from dbgr import request, response


@request
async def posts(env, session):
    ''' Retrieve all posts '''
    await session.get(f'{env["placeholder"]["url"]}/posts')


@request
async def post(env, session, post_id: int=1):
    ''' Retrieve post by ID '''
    res = await session.get(f'{env["placeholder"]["url"]}/posts/{post_id}')
    return await res.json()


@request
async def last_post_id(env, session) -> int:
    ''' Retrieve id of latest post '''
    res  = await session.get(f'{env["placeholder"]["url"]}/posts')
    data = await res.json()
    return data[-1]['id']


@request
async def delete_post(env, session, post_id: int):
    ''' Delete post by ID '''
    await session.delete(f'{env["placeholder"]["url"]}/posts/{post_id}')


@request
async def post_comments(env, session, post_id: int=1):
    ''' Retrieve comments from single post '''
    res = await session.get(
        f'{env["placeholder"]["url"]}/comments', params={'postId': post_id}
    )
    return await res.json()


@request
async def last_post_comments(session):
    ''' Retrieve comments from latest post '''
    session.conn_timeout = 2
    last_post_id = await response('last_post_id')
    return await response('post_comments', post_id=last_post_id)


@request
async def user_posts(env, session, user_id: int=1):
    ''' Retrieve comments created by a user '''
    res = await session.get(
        f'{env["placeholder"]["url"]}/posts', params={'userId': user_id}
    )
    return await res.json()


@request
async def create_post(env, session, user_id: int, title: str, body: str) -> int:
    ''' Create new post '''
    res = await session.post(
        f'{env["placeholder"]["url"]}/posts',
        json={
            'title': title,
            'body': body,
            'userId': user_id
        }
    )
    data = await res.json()
    return data['id']


@request
async def patch_post(env, session, post_id: int, title: str, body: str):
    ''' Update posts title and body '''
    await session.patch(
        f'{env["placeholder"]["url"]}/posts/{post_id}',
        json={
            'title': title,
            'body': body,
        }
    )


@request
async def comments(env, session):
    ''' Retrieve all comments '''
    await session.get(f'{env["placeholder"]["url"]}/comments')


@request
async def comment(env, session, comment_id: int=1):
    ''' Retrieve comment by ID '''
    await session.get(f'{env["placeholder"]["url"]}/comments/{comment_id}')


@request
async def delete_comment(env, session, comment_id: int):
    ''' Delete comment by ID '''
    await session.delete(f'{env["placeholder"]["url"]}/comments/{comment_id}')


@request
async def albums(env, session):
    ''' Retrive all albums '''
    await session.get(f'{env["placeholder"]["url"]}/albums')


@request
async def album(env, session, album_id: int=1):
    ''' Retrieve album by ID '''
    await session.get(f'{env["placeholder"]["url"]}/albums/{album_id}')


@request
async def delete_album(env, session, album_id: int):
    ''' Delete album by ID '''
    await session.delete(f'{env["placeholder"]["url"]}/albums/{comment_id}')


@request
async def photos(env, session):
    ''' Retrive all photos '''
    await session.get(f'{env["placeholder"]["url"]}/photos')


@request
async def photo(env, session, photo_id: int=1):
    ''' Retrive photo by ID '''
    await session.get(f'{env["placeholder"]["url"]}/photos/{photos}')


@request
async def delete_photo(env, session, photo_id: int):
    ''' Delete photo by ID '''
    await session.delete(f'{env["placeholder"]["url"]}/photos/{photo_id}')


@request
async def todos(env, session):
    ''' Retrieve all todos '''
    await session.get(f'{env["placeholder"]["url"]}/todos')


@request
async def todo(env, session, todo_id: int=1):
    ''' Retrieve todo by ID '''
    await session.get(f'{env["placeholder"]["url"]}/todo/{todo_id}')


@request
async def delete_todo(env, session, todo_id: int):
    ''' Delete todo by ID '''
    await session.delete(f'{env["placeholder"]["url"]}/todo/{todo_id}')


@request
async def users(env, session):
    ''' Retrieve all users '''
    await session.get(f'{env["placeholder"]["url"]}/users')


@request
async def user(env, session, user_id: int=1):
    ''' Retrive user by ID '''
    await session.get(f'{env["placeholder"]["url"]}/users/{user_id}')


@request
async def delete_user(env, session, user_id: int):
    ''' Delete user by ID '''
    await session.delete(f'{env["placeholder"]["url"]}/users/{user_id}')
