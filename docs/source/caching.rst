.. _caching:

Caching
=======
You can mark request to be cached. All subsequent calls of the same request will
be suspended and the result will be taken from cache. This is useful for example
when you work with API that requires sign-in. You usually want to call the authentication
endpoint only once at the beginning and then just re-use cached value.

To enable caching call ``@request`` decorator with ``cache`` argument and type of
cache you want to use for this request:

.. code-block:: python

    @request
    async def get_jwt(session, username, password:secret) -> secret:
        res = await session.post(f'https://example.com/login', data={
            'username': username,
            'password': password
        )}
        data = return await res.json()
        return data['jwt']

.. code-block:: bash

    $ dbgr interactive
    Dbgr interactive mode; press ^C to exit.
    > get_jwt
    > POST https://example.com/login
    < 200 OK
    < Result (str):
      e******************c
    > get_jwt
    < Result (str, from cache):
      e******************c


There is only one supported cache type at this moment: ``session``. This type stores
the result in memory for the time the program is running. This is not very useful
when you execute requests one by one. But in interactive mode, the value is cached
until you terminate DBGR.

.. tip::
    The cache key is constructed from the request and values of all arguments. If you
    call cached request with different arguments, it will get executed.

If you call :func:`dbgr.response` with ``cache=False`` while you already have a
result in cache, the request will get executed and new value will be stored in cache.

.. code-block:: python

    @request
    async def list_comments(session):
        auth = await response('get_jwt', cache=False) # This will always result in HTTP call
        # ...
