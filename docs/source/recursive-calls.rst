.. _recursive_calls:

Recursive Calls
===============
Sometimes you might need to make a different request before executing what you really
want to do. For example, to download user data, you need to login first. You can do
that by using coroutine :func:`dbgr.response`.

.. warning::
    DBGR doesn't detect or prevent recursion. Be careful not to unintentionally
    cause DDoS on your (or someone else's) servers.

Response accepts one required argument - the name of the request to execute as
string:

.. function:: dbgr.response(request_name, env=None, session=None, use_defaults=False, cache=True, \*\*kwargs)

    Coroutine to make recursive requests.

    All kwargs will be mapped to arguments required by target request.
    Kwargs that are not required by target request will be ignored.

    :param str request_name:
        Name of fully qualified name of a request to execute

    :param configparser.ConfigParser environment:
        Instance of :class:`configparser.ConfigParser` with loaded environment variables.
        Pass this argument only if you want to call request with environment different
        from current one. (optional)

    :param aiohttp.ClientSession session:
        Instance of :class:`aiohttp.ClientSession` that will be used to make requests.
        Leave the argument empty, if you want to use current session. (optional)

    :param bool use_defaults:
        Boolean flag if DBGR should use default argument value wherever possible.
        It's equivalent for to using ``--use-defaults`` in terminal. More about it in
        :ref:`Arguments section<arguments_default_value>`. (optional)

    :param bool cache:
        Boolean flag if DBGR should use return value from cache, if available. Applicable
        only to requests with cache turned on. More about it in
        :ref:`Cache section<caching>`. (optional)

.. code-block:: python

    from dbgr import request, response, secret

    @request
    async def login(session, username, password:secret) -> secret:
        res = await session.post('https://example.com/login', data={
            'username': username,
            'password': password
        )
        data = await res.json()
        return data['jwt']

    @request
    async def get_profile(session):
        jwt = await response('login')
        res = await session.get('https://example.com/profile/me', headers={
            'Authorization': f'Bearer {jwt}'
        })

.. code-block:: bash

    $ dbgr r get_profile
    username: jakub@tesarek.me
    password [type: secret]:
    > POST https://example.com/login
    < 200 OK
    Result (string):
    c*********************e

    > GET https://example.com/profile/me
    > 200 OK

.. tip::
    You can call requests with fully qualified name
    :ref:`in the same way you do when calling requests from terminal<executing_requests>`.
