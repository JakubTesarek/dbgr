.. _arguments:

Arguments
=========

Environment and Session
-----------------------
In the example requests above, the requests we created accepted two arguments:
``env`` and ``session``. Env is a instance of ``configparser.ConfigParser`` created
from your environment file.  Session is instance of ``aiohttp.ClientSession``.

Both of those arguments are optional, you can write requests that don't need them.
But if you use them, they have to be in the fist two arguments and named exactly
``env`` and ``session``.

.. _custom_arguments:

Custom Arguments
----------------
Besides environment and session, you can add any number of your own arguments. DBGR
will prompt you for the value when you execute the request.

.. code-block:: python

    @request
    async def post(env, session, post_id):
        await session.get(f'{env["placeholder"]["url"]}/posts/{post_id}')

.. code-block:: bash

    $ dbgr r post
    post_id: 1
    > GET http://jsonplaceholder.typicode.com/post/1
    < 200 OK
    <
    < Headers:
    <  Date: Mon, 10 Jun 2019 10:07:28 GMT
    <  Content-Type: application/json; charset=utf-8
    <  Transfer-Encoding: chunked
    <  Connection: keep-alive
    <  Expires: Mon, 10 Jun 2019 14:07:28 GMT
    <  Content-Encoding: gzip
    <
    < Content (application/json; charset=utf-8):
    {
        "body": "quia et suscipit\nsuscipit recusandae consequuntur",
        "id": 1,
        "title": "sunt aut facere repellat provident",
        "userId": 1
    }

You can check what arguments a request accepts by running ``dbgr l``:

.. code-block:: bash

    $ dbgr l
    placeholder:
     - post
       id

You can specify some or all values for custom arguments when you execute requests
with ``--arg <key>=<value>``. DBRG will not prompt you for values it already has:

.. code-block:: bash

    $ dbgr r post --arg post_id=1
    > GET http://jsonplaceholder.typicode.com/post/1
    < 200 OK
    <
    < Headers:
    <  Date: Mon, 10 Jun 2019 10:07:28 GMT
    <  Content-Type: application/json; charset=utf-8
    <  Transfer-Encoding: chunked
    <  Connection: keep-alive
    <  Expires: Mon, 10 Jun 2019 14:07:28 GMT
    <  Content-Encoding: gzip
    <
    < Content (application/json; charset=utf-8):
    {
        "body": "quia et suscipit\nsuscipit recusandae consequuntur",
        "id": 1,
        "title": "sunt aut facere repellat provident",
        "userId": 1
    }

.. _arguments_default_value:

Default Value
-------------
Arguments can have default value so that when you get prompted for the value, you
can just hit enter to accept it.

.. code-block:: python

    @request
    async def post(env, session, post_id=1):
        await session.get(f'{env["placeholder"]["url"]}/posts/{post_id}')

.. code-block:: bash

    $ dbgr r post
    post_id [default: 1]: #just hit enter
    > GET http://jsonplaceholder.typicode.com/post/1
    < 200 OK

If you know you want to use all the default values and don't want DBGR to prompt
you, use argument ``--use-defaults``.


.. code-block:: bash

    $ dbgr r post --use-defaults
    > GET http://jsonplaceholder.typicode.com/post/1
    < 200 OK

.. _arguments_type_hinting:

Type Hinting
------------
By default, DBGR will pass all values of arguments as strings. You can change the
type with `type hinting`_. DBGR will try to convert given value to the type you
specify, giving you an error message when it fails.

.. _type hinting: https://docs.python.org/3/library/typing.html

.. code-block:: python

    @request
    async def post(env, session, post_id:int=1):
        await session.get(f'{env["placeholder"]["url"]}/posts/{post_id}')

.. code-block:: bash

    $ dbgr r post
    post_id [default: 1, type:int]: abc
    String "abc" cannot be converted to int
    post_id [default: 1, type:int]: 1
    > GET http://jsonplaceholder.typicode.com/post/1
    < 200 OK

All the types available for type hinting are described in :ref:`types`. Any unrecognized
type will be ignored.

.. _arguments_order:

Order of Precedence of Arguments
--------------------------------
There is many way to specify value for arguments. It's important to understant in
which order they get resolved.

1. First DBGR will take all the values specified with ``--arg`` in ``dbgr r`` command and assigns them.
2. If you used ``--use-defaults`` DBGR will assign default value to every argument that has one.
3. DBGR  will prompt you for values for all remaining arguments.
