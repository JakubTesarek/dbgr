DBGR: HTTP client that gives you full control
=============================================

Dbgr [read 'ˌdiːˈbʌɡər'] is a interactive terminal tool to test and debug HTTP APIs.
It offers alternative to Postman_, Insomnia_ and other HTTP clients. It is designed
for programmers that prefer to use code instead of graphical tools and want full control
over their HTTP requests.

.. _postman: https://www.getpostman.com/
.. _insomnia: https://insomnia.rest/


Installation
------------
The easiest way to install DBGR is via Pypi_:

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



.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
