.. _types:

Types
=====
Type hinting provides you a way to specify types of :ref:`arguments` your requests
expect as well as their return value. DBGR will try to convert any input to the given
type.

To specify a type of an argument, use Pythons build in `type hinting`_:

.. _type hinting: https://docs.python.org/3/library/typing.html

.. code-block:: python

    from datetime import datetime
    from dbgr import request

    @request
    async def post_publish_time(env, session, post_id:int) -> datetime:
        # type(post_id) == int
        res = await session.get(f'{env["placeholder"]["url"]}/posts/{post_id}')
        data = await res.json()
        return data['publish-datatime'] # will convert to datetime.datetime

.. _primitive_types:

Primitive Types
---------------
DBGR supports these primitive types: ``int``, ``float`` and ``str``. (Type
``bool`` is decribed in :ref:`separate section<boolean_type>`)

.. _boolean_type:

Boolean Type
------------
When you specify an argument or return value to be a ``bool``, DBGR will convert these
values (and their variants in different case) to ``False``: ``False``, ``0``, ``"f"``,
``"false"``, ``"n"``, ``"no"``. Also all objects implementing ``__bool__`` method will
be converted to the return value of that method. For example, empty colletion will
convert to ``False``. All other values will be converted to ``True``.

.. code-block:: python

    from dbgr import request

    @request
    async def have_new_messages(env, session, post_id:int) -> bool:
        res = await session.get(f'{env["placeholder"]["url"]}/posts/{post_id}')
        return await res.json() # empty list will return False, True otherwise

.. _secret_type:

Secret Type
-----------
Type ``dbgr.secret`` is resolved the same as ``str`` with the difference that when prompted,
DBGR will hide the value you are typing. Also the secret return value of a request will
printed as obfuscated in the terminal.

.. warning::
    DBGR will not obfuscate the value if it appears somewhere in request log, eg. headers.*

.. code-block:: python

    from dbgr import request, secret

    @request
    async def get_jwt(session, username, password:secret) -> secret:
        res = await session.post(f'https://example.com/login', data={
            'username': username,
            'password': password
        )}
        data = return await res.json()
        return data['jwt']

.. code-block:: bash

    $ dbgr r get_jwt
    > POST https://example.com/login
    < 200 OK
    < Result (str):
      e******************c

.. _calendar_types:

Calendar Types
--------------
DBGR implements set of calendar types: ``datetime.time``, ``datetime.date``, ``datetime.time``.
They allow you to input date and time in human readable format. In background it
uses `dateparser module`_ and supports all formats from that module.

.. _dateparser module: https://dateparser.readthedocs.io/en/latest/

All calendar types accept strings but also another instances of ``datetime`` types.
Missing parts will be filled-in with current value as the table bellow shows.

+-----------+-------------+------------------------------+
| Used type | Input value | Output value                 |
+===========+=============+==============================+
| datetime  | datetime    | input value directly         |
+-----------+-------------+------------------------------+
| datetime  | date        | input date with current time |
+-----------+-------------+------------------------------+
| datetime  | time        | input time with current date |
+-----------+-------------+------------------------------+
| date      | datetime    | date from input datetime     |
+-----------+-------------+------------------------------+
| date      | date        | input value directly         |
+-----------+-------------+------------------------------+
| date      | time        | current date                 |
+-----------+-------------+------------------------------+
| time      | datetime    | time from input datetime     |
+-----------+-------------+------------------------------+
| time      | date        | current time                 |
+-----------+-------------+------------------------------+
| time      | time        | input value directly         |
+-----------+-------------+------------------------------+

.. code-block:: python

    from datetime import datetime
    from dbgr import request

    @request
    async def publish_article(session, article_id: int, publish_date: datetime):
        await session.patch(f'https://example.com/article/{article_id}', data={
            'publish_datetime': datetime.isoformat()
        )}

.. code-block:: bash

    $ dbgr r publish_article
    article_id [type: int]: 1
    publish_date [type: datetime]: tomorrow # tomorrow date with current time
    > PATCH
    < 201 No Content
