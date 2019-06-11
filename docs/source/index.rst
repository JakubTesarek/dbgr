DBGR: HTTP client that gives you full control
=============================================

Dbgr [read 'ˌdiːˈbʌɡər'] is a interactive terminal tool to test and debug HTTP APIs.
It offers alternative to Postman_, Insomnia_ and other HTTP clients. It is designed
for programmers that prefer to use code instead of graphical tools and want full control
over their HTTP requests.

.. _postman: https://www.getpostman.com/
.. _insomnia: https://insomnia.rest/


.. _installation:

Installation
------------
The easiest way to install DBGR is via Pypi_:

.. _pypi: https://pypi.org/project/dbgr/

.. code-block:: bash

    $ pip install dbgr
    $ dbgr -v
    1.1.0

DBGR requires Python >=3.6.

.. _quick_start:

Quick Start
-----------
First step when working with DBGR is to create a directory which will DBGR search
for requests and environment settings.

.. code-block:: bash

    $ mkdir quickstart
    $ cd quickstart

Inside create your default environment file ``default.ini``. For now just place
a section header inside:

.. code-block:: ini

    [default]

Now create another file, call it ``quickstart.py`` and place create your first request:

.. code-block:: python

    from dbgr import request

    @request
    async def get_example(session):
        await session.get('http://example.com')


You can also `download the quickstart from Github`_.

.. _download the quickstart from github: https://github.com/JakubTesarek/dbgr/tree/master/examples/quickstart

You can check that DBGR registered the request by running ``dbgr list``:

.. code-block:: bash

    $ dbgr list
    quickstart:
     - get_example

To execute it, run ``dbgr request get_example``:

.. code-block:: bash

    $ dbgr request get_example
    > GET http://example.com
    < 200 OK
    <
    < Headers:
    <  Content-Encoding: gzip
    <  Cache-Control: max-age=604800
    <  Content-Type: text/html; charset=UTF-8
    <  Date: Mon, 10 Jun 2019 09:47:15 GMT
    <  Etag: "1541025663+gzip"
    <  Expires: Mon, 17 Jun 2019 09:47:15 GMT
    <  Last-Modified: Fri, 09 Aug 2013 23:54:35 GMT
    <  Server: ECS (dcb/7F5E)
    <  Vary: Accept-Encoding
    <  X-Cache: HIT
    <  Content-Length: 606
    <
    < Content (text/html; charset=UTF-8):
    Result (NoneType)


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    requests
    arguments
    return-value
    types
    recursive-calls
    caching
    asserts
    environment
    terminal-interface
    help
    contributing
    licence


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
