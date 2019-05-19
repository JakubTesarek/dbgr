# DBGR
Dbgr [read 'debugger'] is a terminal tool to test and debug Http APIs.

## Project setup
To setup a project create new directory and inside create .py file with this content:

```
from dbgr import request

@request
async def get_example(env, session):
    await session.get('http://example.com')
```

You've not created your firts request. You can execute it with `$ dbgr request get_example` or shorter `$ dbgr r get_example`.

## Requests
DBGR request is a function decorated with `@dbgr.request`. It accepts two arguments. First agument is a disctionary with your environment. Second arguement is a instance of `aiohttp.ClientSession`. You don't have to return or log anything from your request. The ClientSession does it automatically.

### Names
By default you execute your request with `$ dbgr r <function_name>`. Optinally you can change the name of the request with an argument:

```
@requst(name='different_name')
async def get_example(env, session):
    await session.get('http://example.com')
```

And then you'll execute it with alternative name `$ dbgr r different_name`. Name of a request can contain only letters, numbers and/or underscores. Names are case sensitive.

DBGR automatically loads all requests from all .py files in current directory which can leads to collisions in names. Therefore you can execute the endpoint with fully qualified name including module name: `$ dbgr r module:function`. Module name is simply name of the file without extension.

## Environment
Environments enable you to define variables, eg. different urls, and then run your requests with different arguments. Your default environment is placed in `default.ini`. This is a file in ini format using [ExtendedInterpolation](https://docs.python.org/3/library/configparser.html#configparser.ExtendedInterpolation).

## Recursive calls
Sometimes you might need to make a different requests before executing what you really want to do. For example to download user data, you need to login first. You can do that by using coroutine `dbgr.response`. It accepts 3 arguments - name of the request to execute (you can specify module the same as in terminal), environment and session.

In most cases you'll call it with the session and environment your function received. But you can also modify them before calling `response`.

```
from dbgr import request, response

@request
async def login(env, session):
    rv = session.post('...login')
    return await rv.json()

@request
async def get_data(env, session):
    auth = response('login', env, session)
    data = session.get('...data', headers={'Authorization': f'Bearer {auth["token"}'})
```

** DBGR doens't try to detect reccursion. Be carefull to unintentionaly cause DDoS on your servers. **

## Caching
You can mark request to be cached in memory. All subsequent calls of the same request will be suspended and the result will be taken from cache. This is usefull for example when you work with API that requires sign-in. You usually want to call the authentication endpoint only once at the beginning and then just re-use cached value.

To enable caching call `@request` decorator with `cache` argument.

```
@request(cache='session')
async def login(env, session):
    ...
```

There is only one supported cache type at this moment: `session`. This type stores the result in memory for the time the program is running. This is not very usefull when you execute requests one by one. But in interactive mode, the value is cached until you exit the program.


## Autocomplete and History
DBGR supports autocomplete for commands and requests. You need to install and setup [argcomplete](https://pypi.org/project/argcomplete/) according to documentation.

Interactive mode supports terminal history.
