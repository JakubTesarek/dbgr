.. _asserts:

Aserts
======

DBGR supports assertions in requests. If an assert fails, it will get reported to the terminal.

.. code-block:: python

    @request
    async def create_item(session):
        rv = session.get('http://example.com/not_found')
        assert rv.status == 200

.. code-block:: bash

    > GET http://example.com
    > 200 OK
    >
    > Request headers:
    >  Host: example.com
    >  Accept: */*
    >  Accept-Encoding: gzip, deflate
    >  User-Agent: Python/3.6 aiohttp/3.5.4
    <
    < Response headers:
    <  Content-Encoding: gzip
    <  Accept-Ranges: bytes
    <  Cache-Control: max-age=604800
    <  Content-Type: text/html; charset=UTF-8
    <  Date: Wed, 12 Jun 2019 07:01:06 GMT
    <  Etag: "1541025663"
    <  Expires: Wed, 19 Jun 2019 07:01:06 GMT
    <  Last-Modified: Fri, 09 Aug 2013 23:54:35 GMT
    <  Server: ECS (dcb/7EA2)
    <  Vary: Accept-Encoding
    <  X-Cache: HIT
    <  Content-Length: 606
    Assertion error in my_module.py:12:
    assert res.status == 200

