.. _return_value:

Return Value
============
Your request can return a value. This return value will be printed to the terminal
when you execute a request. It also gets returned when you use
:ref:`recursive_calls`. This can be useful for example for authentication.

.. hint::
    The return value also get cached when :ref:`caching` is implemented.

The :ref:`types` that can be used are the same for arguments.


Secret Return Value
-------------------
If your request returns :ref:`secret_type`, it will be obfuscated in the terminal output:

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
