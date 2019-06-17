.. _environment:

Environment
===========
Environments offer you different way to specify variables for your requests. Your
default environment is placed in ``default.ini``. This is a file in `ini format`_
using ExtendedInterpolation_.

.. _extendedinterpolation: https://docs.python.org/3/library/configparser.html#configparser.ExtendedInterpolation).
.. _`ini format`: https://docs.python.org/3/library/configparser.html

.. code-block:: ini

    [DEFAULT]
    url: http://127.0.0.1
    login: test@example.com
    user_agent: Chrome/74.0.3729.169
    timeout: 5

    [login_service]
    url: ${DEFAULT:url}/login
    timeout: 10

    [admin]
    url: ${DEFAULT:url}/admin

When you execute a request, the current environment file get parsed and passed in
variable ``env`` to your request coroutine. This allows you to test your request
against multiple environments, for example production and staging and observe if
they behave the same.

You can change the environment that will be used with ``-e``/``--env`` switch. DBGR
searches for environments in current working directory in `.ini` files. Name of the
environment is the name of the file without suffix.

You can list all available environments with ``dbgr envs``/``dbgr e``. With optional
argument (``dbgr e <name_of_environment>``) it will list all variables defined in
that environment.

