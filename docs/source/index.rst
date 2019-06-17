DBGR: HTTP client that gives you full control
=============================================

|PyPI version| |License| |Build Status| |Code Coverage| |Documentation Status|

.. |PyPI version| image:: https://badge.fury.io/py/dbgr.svg
   :target: https://badge.fury.io/py/dbgr
.. |License| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
.. |Build Status| image:: https://travis-ci.org/JakubTesarek/dbgr.svg?branch=master
   :target: https://travis-ci.org/JakubTesarek/dbgr
.. |Code Coverage| image:: https://codecov.io/gh/JakubTesarek/dbgr/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/JakubTesarek/dbgr
.. |Documentation Status| image:: https://readthedocs.org/projects/dbgr/badge/?version=latest
   :target: https://dbgr.readthedocs.io/en/latest/?badge=latest

Dbgr [read ``'ˌdiːˈbʌɡər'``] is a interactive terminal tool to test and debug HTTP APIs.
It offers alternative to Postman_, Insomnia_ and other HTTP clients. It is designed
for programmers that prefer to use code instead of graphical tools and want full control
over their HTTP requests.

.. _postman: https://www.getpostman.com/
.. _insomnia: https://insomnia.rest/

.. _features:

Features
--------
- :ref:`Terminal interface with autocomplete and bash history<terminal_interface>`
- :ref:`Full control over your requests with Python<requests>`
- :ref:`Recursive calls<recursive_calls>`
- :ref:`Local caching of responses<caching>`
- :ref:`Customizable interface<types>`

|screencast|

.. |screencast| image:: https://asciinema.org/a/tnDyDebgMmwwVBTUX8M2OrJ4a.svg
        :alt: DBGR Basic Usage Example
        :target: https://asciinema.org/a/tnDyDebgMmwwVBTUX8M2OrJ4a?autoplay=1

.. _installation:

Installation
------------
The easiest way to install DBGR is via PyPi_:

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

.. tip::
    You can also `download the quickstart from Github`_.

.. _download the quickstart from github: https://github.com/JakubTesarek/dbgr/tree/master/examples/quickstart

You can check that DBGR registered the request by running ``dbgr list``:

.. code-block:: bash

    $ dbgr list
    quickstart:
     - get_example

To execute it, run ``dbgr request get_example``:

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
    <  Date: Sun, 16 Jun 2019 15:29:41 GMT
    <  Last-Modified: Fri, 09 Aug 2013 23:54:35 GMT
    <  Content-Length: 606
    <
    < Response data (text/html):
    <!doctype html>
    <html>
    <head>
        <title>Example Domain</title>
        <meta charset="utf-8" />
        <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
    </head>

    <body>
    <div>
        <h1>Example Domain</h1>
        <p>This domain is established to be used for illustrative examples in documents. You may use this
        domain in examples without prior coordination or asking for permission.</p>
        <p><a href="http://www.iana.org/domains/example">More information...</a></p>
    </div>
    </body>
    </html>
    Result (NoneType)

.. tip::
    Example outputs in this documentation are shortened for readability.
    Output from DBGR on your computer will contain the whole response.

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
    license


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
