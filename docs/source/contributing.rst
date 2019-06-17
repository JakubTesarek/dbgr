.. _contributing:

Contributing
============
Thank considering your contribution to DBGR. Any help or feedback is greatly appreciated.

Development setup
-----------------
If you want to develop debugger locally, there is an alternative installation process
that will make this experience easier.

First, `fork DBGR repository`_. Then you can clone the forked repository and create
local environment:

.. _`fork DBGR repository`: https://help.github.com/en/articles/fork-a-repo

.. code-block:: bash

    $ git clone https://github.com/<your_username>/dbgr
    $ cd dbgr
    $ virtualenv env3.7 --python=python3.7
    $ source env3.7/bin/activate
    (env3.7) $ pip install -r requirements.txt -r requirements-dev.py

.. tip::
    The process for setting up python 3.6 is the same, just use different python executable.

Now you can install DBGR from local directory:

.. code-block:: bash

    $ source env3.7/bin/activate
    (env3.7) $ pip install -e .


Testing
-------
.. code-block:: bash

    (env3.7) $ make test

This will run all unit-tests and generate coverage report. 100% test coverage is
mandatory.

.. tip::
    The file ``Makefile`` contains other commands that can be useful when developing
    DBGR. Run ``make`` to see all the available commands.

Linting
-------
.. code-block:: bash

    (env3.7) $ make lint

DBGR user pylint_ with some lints disabled. See ``.pylintrc`` for details. Score
of 10.0 is mandatory.

.. _pylint: https://www.pylint.org/

Building documentation
----------------------
This documentation was build using Sphinx_. To build it locally, run:

.. _sphinx: http://www.sphinx-doc.org/en/master/

.. code-block:: bash

    (env3.7) $ make documentation
    (env3.7) $ open open docs/build/html/index.html

All new features and changes have to be documented.

Before committing please spell-check the documentation using:

.. code-block:: bash

    (env3.7) $ make spelling

If Sphinx reports a spelling mistake on a word you are sure is spelled correctly,
add it to ``docs/source/spelling.txt``. Sort the file alphabetically.

Building distribution
---------------------
These steps are mandatory only when preparing for release. Individual developers don't
need to worry about them.

1. Run all tests, make sure they all pass and the code coverage is 100%.
2. Move appropriate changes from ``# Unreleased`` section in ``CHANGELOG.rst`` to new version.
3. Change version in ``dbgr/meta.py``
4. Build distribution, make sure there are no errors

    .. code-block:: bash

        (env3.7) $ make build

5. Tag new version on GitHub
6. Create new `GitHub release`_

    - Upload content of ``dist``
    - Copy latest changes from ``CHANGELOG.rst`` to release description

7. Upload content of ``dist`` to PyPi_.

    .. code-block:: bash

        (env3.7) $ make publish

.. _`github release`: https://github.com/JakubTesarek/dbgr/releases/new
.. _`pypi`: https://pypi.org/project/dbgr/

Links
-----
- `DBGR Github repository`_
- `DBGR on PyPi`_
- `Issue tracker`_ (`good onboarding issues`_)
- `Travis-io build job`_
- `Codev - test coverage statistics`_
- `DBGR on Source Rank`_
- `Keep a Changelog - changelog format used by DBGR`_
- `Asciinema - terminal recording`_

.. _`dbgr github repository`: https://github.com/JakubTesarek/dbgr
.. _`dbgr on pypi`: https://pypi.org/project/dbgr/
.. _`issue tracker`: https://github.com/JakubTesarek/dbgr/issues
.. _`good onboarding issues`: https://github.com/JakubTesarek/dbgr/labels/good%20first%20issue
.. _`travis-io build job`: https://travis-ci.org/JakubTesarek/dbgr
.. _`codev - test coverage statistics`: https://codecov.io/gh/JakubTesarek/dbgr
.. _`dbgr on source rank`: https://libraries.io/pypi/dbgr/sourcerank
.. _`keep a changelog - changelog format used by dbgr`: https://keepachangelog.com/en/1.0.0/
.. _`asciinema - terminal recording`: https://asciinema.org/
