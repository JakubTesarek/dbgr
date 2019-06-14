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

Dbgr [read 'ˌdiːˈbʌɡər'] is a interactive terminal tool to test and debug HTTP APIs.
It offers alternative to Postman_, Insomnia_ and other HTTP clients. It is designed
for programmers that prefer to use code instead of graphical tools and want full control
over their HTTP requests.

.. _postman: https://www.getpostman.com/
.. _insomnia: https://insomnia.rest/

   `Full documentation can be found on Read the Docs`_

.. _`full documentation can be found on read the docs`: https://dbgr.readthedocs.io/en/latest/

Features
--------
- `Terminal interface with autocomplete and bash history`_
- `Full control over your requests with Python`_
- `Recursive calls`_
- `Local caching of responses`_
- `Customizable interface`_

.. _`Terminal interface with autocomplete and bash history`: https://dbgr.readthedocs.io/en/latest/terminal-interface.html
.. _`Full control over your requests with Python`: https://dbgr.readthedocs.io/en/latest/requests.html#requests
.. _`Recursive calls`: https://dbgr.readthedocs.io/en/latest/recursive-calls.html#recursive-calls
.. _`Local caching of responses`: https://dbgr.readthedocs.io/en/latest/caching.html
.. _`Customizable interface`: https://dbgr.readthedocs.io/en/latest/types.html#types

|screencast|

.. |screencast| image:: https://asciinema.org/a/uNs262JVwxY2d1BGZTdRvDsWH.svg
        :alt: DBGR Basic Usage Example
        :target:https: //asciinema.org/a/uNs262JVwxY2d1BGZTdRvDsWH

Installation
------------
The easiest way to install DBGR is via PyPi_:

.. _pypi: https://pypi.org/project/dbgr/

.. code-block:: bash

    $ pip install dbgr
    $ dbgr -v
    1.1.0

DBGR requires Python >=3.6.

Quick Start
-----------
First step when working with DBGR is to create a directory which will DBGR search
for requests and environment settings.

   You can also `download the quickstart from Github`_.

.. _download the quickstart from github: https://github.com/JakubTesarek/dbgr/tree/master/examples/quickstart


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


`Read the full documentation on Read the Docs`_

.. _`read the full documentation on read the docs`: https://dbgr.readthedocs.io/en/latest/
