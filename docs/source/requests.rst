.. _requests:

Requests
========

Request is a coroutine decorated with ``@dbgr.requests``. DBGR searches all ``.py``
files in currect directory and register all requests. You can check which requests
DBGR sees by running ``dbgr list``:

.. code-block:: python

   from dbgr import request

   @request
   async def posts(env, session):
      ''' Retrieve all posts '''
      await session.get(f'{env["placeholder"]["url"]}/posts')

   @request
   async def post(env, session, post_id: int=1):
       ''' Retrieve post by ID '''
       res = await session.get(f'{env["placeholder"]["url"]}/posts/{post_id}')
       return await res.json()

.. code-block:: bash

    $ dbgr list
    placeholder:
     - posts
       Retrieve all posts
     - post
       Retrieve post by ID
       Arguments:
        - post_id [default: 1, type: int]

.. _executing_requests:

Executing Requests
------------------
To execute a request, use ``dbgr request <name_of_request>`` (or shorter ``dbgr r``).
Name of request is simply a name of the decorated coroutine.

.. code-block:: bash

    $ dbgr request posts
    > GET http://jsonplaceholder.typicode.com/posts
    > 200 OK
    >
    > Request headers:
    >  Host: jsonplaceholder.typicode.com
    >  Accept: */*
    >  Accept-Encoding: gzip, deflate
    >  User-Agent: Python/3.6 aiohttp/3.5.4
    <
    < Response Headers:
    <  Date: Mon, 10 Jun 2019 10:07:28 GMT
    <  Content-Type: application/json; charset=utf-8
    <  Transfer-Encoding: chunked
    <  Connection: keep-alive
    <  Expires: Mon, 10 Jun 2019 14:07:28 GMT
    <  Content-Encoding: gzip
    <
    < Response data (application/json; charset=utf-8):
    [
      {
        "body": "quia et suscipit\nsuscipit recusandae consequuntur",
        "id": 1,
        "title": "sunt aut facere repellat provident",
        "userId": 1
      }
    ]

DBGR will execute your coroutine and print response from the server. If the response
is json, xml or other format that DBGR recognizes, it will be formated and printed
as well.

Sometimes you will have two different requests with the same name in two different
modules. DBGR can still execute them but you have to specify in which module it should
search. Module name is simply the name of the file without ``.py``.

.. code-block:: bash

    $ dbgr request posts
    Request "posts" found in multiple modules: placeholder, another_module
    $ dbgr request placeholder:posts
    > GET http://jsonplaceholder.typicode.com/posts
    > 200 OK
    >
    > Request headers:
    >  Host: jsonplaceholder.typicode.com
    >  Accept: */*
    >  Accept-Encoding: gzip, deflate
    >  User-Agent: Python/3.6 aiohttp/3.5.4
    <
    < Response headers:
    <  Date: Mon, 10 Jun 2019 10:07:28 GMT
    <  Content-Type: application/json; charset=utf-8
    <  Transfer-Encoding: chunked
    <  Connection: keep-alive
    <  Expires: Mon, 10 Jun 2019 14:07:28 GMT
    <  Content-Encoding: gzip
    <
    < Response data (application/json; charset=utf-8):
    [
      {
        "body": "quia et suscipit\nsuscipit recusandae consequuntur",
        "id": 1,
        "title": "sunt aut facere repellat provident",
        "userId": 1
      }
    ]

If you want to use different name from the coroutine name, you can set it explicitly
in a parameter of ``@dbgr.request``:

.. code-block:: python

   from dbgr import request

   @request(name='alternative_name')
   async def posts(env, session):
      ''' Retrieve all posts '''
      await session.get(f'{env["placeholder"]["url"]}/posts')

.. code-block:: bash

    $ dbgr list
    placeholder:
     - alternative_name
       Retrieve all posts
     - post
       Retrieve post by ID
       Arguments:
        - post_id [default: 1, type: int]

The rules for explicit names are the same as for names of python functions.
