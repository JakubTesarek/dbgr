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

## Arguments
When defining your request, you can specify any number of arguments that it will accept. These arguments will be filled with values specified when you call your request. If you don't provide them in terminal, DBGR will prompt you for value. You can also define default values for some or all arguments.

```
@request
async def many_arguments(env, session, a1, a2, a3='default'):
    pass
```

When you call this request from terminal, you will be prompted for all 3 arguments. For a3 you will be offered to use default value:

```
$ dbgr r many_arguments
a1:
a2:
a3 [default]:
```

You can provide some values when you execute your request with `-a` or `--arg`:

```
$ dbgr r many_arguments -a a1=foo
a2:
a3 [default]:
```

```
$ dbgr r many_arguments -a a1=foo -a a3=bar
a2:
```

When you call DBGR with `-d` or `--use-defaults` swith, you will prompted only for arguments without default valus:

```
$ dbgr r many_arguments -d
a1:
a2:
```

And finally, you can combine everything together:

```
$ dbgr r many_arguments -d -a a1=foo
a2:
```

### Order of precedence of arguments
1. If you provide argument with `-a`, it will always be used and you will not be prompted.
2. If you use `-d`, dbgr will use default values when possible. You will not be prompted for such arguments.
3. You will get prompted for arguments with default values. Hitting enter without any input will use default value.
4. You will get prompted for arguments without default values. Hitting enter without any input will result in empty string being used.


## Environment
Environments offere you different way to specify variables for your requests. Your default environment is placed in `default.ini`. This is a file in ini format using [ExtendedInterpolation](https://docs.python.org/3/library/configparser.html#configparser.ExtendedInterpolation).

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


### Arguments
As with the terminal execution, you can provide arguments for recursive calls. Simply add them as extra arguments:


```
@request
async def login(env, session, username):
    rv = session.post('...login')
    return await rv.json()

@request
async def get_data(env, session):
    auth = response('login', env, session, username='admin@example.com')
    data = session.get('...data', headers={'Authorization': f'Bearer {auth["token"}'})
```

You can also specify you want to use default values wherever possible with `use_defaults`:

```
@request
async def list_comments(env, session, page=1):
    rv = session.get('/comments', params={page: page})
    return await rv.json()

@request
async def export_comments(env, session):
    auth = response('login', env, session, use_defaults=True)
```

Order of precedence is the same as in terminal execution. You will still get promted for arguments witch don't have any value.


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
