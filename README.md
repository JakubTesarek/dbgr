# DBGR
Dbgr [read 'ˌdiːˈbʌɡər'] is a terminal tool to test and debug HTTP APIs.

## Project setup
To setup a project create new directory and inside create .py file with this content:

```
from dbgr import request

@request
async def get_example(env, session):
    await session.get('http://example.com')
```

This is your first request. Next you need an environment in which you can run this. Create another file called `default.ini`. It has to contain only one section called `[DEFAULT]`, otherwise you can keep it empty:

```
[DEFAULT]
```

Now you can execute the request with `$ dbgr request get_example` or shorter `$ dbgr r get_example`.


## Requests
DBGR request is a function decorated with `@dbgr.request`. In its simplest form it accepts two arguments. First agument is the environment it was executed in. The second argument is an instance of `aiohttp.ClientSession`. You don't have to return or log anything from your request. The ClientSession does all logging automatically.

### Names
By default you execute your request with `$ dbgr r <function_name>`. Optinally you can change the name of the request with an argument:

```
@requst(name='different_name')
async def get_example(env, session):
    await session.get('http://example.com')
```

And then you'll execute it with its alternative name `$ dbgr r different_name`.

> Name of a request can contain only letters, numbers and/or underscores. Names are case sensitive.

DBGR automatically loads requests from all .py files in working directory. This can lead to collisions in names. Therefore you can execute the endpoint with fully qualified name including module name: `$ dbgr r module:function`. Module name is simply the name of the file without extension.

## Arguments
When defining your request, you can specify any number of arguments that it will accept (besides env and session). These arguments will be filled with values specified when you call your request. If you don't provide them in the terminal, DBGR will prompt you for value. You can also define default values for some or all arguments.

```
@request
async def many_arguments(env, session, arg1, arg2, arg3='default'):
    pass
```

When you call this request from terminal, you will be prompted for all 3 arguments. For `a3` you will be offered to use default value:

```
$ dbgr r many_arguments
arg1:
arg2:
arg3 [default]:
```

You can provide values when you execute your request with `-a` or `--arg`:

```
$ dbgr r many_arguments -a arg1=foo
arg2:
arg3 [default]:
```

```
$ dbgr r many_arguments -a arg1=foo -a arg3=bar
arg2:
```

When you call DBGR with `-d` or `--use-defaults` swith, you will be prompted only for arguments without default values:

```
$ dbgr r many_arguments -d
arg1:
arg2:
```

And finally, you can combine everything together:

```
$ dbgr r many_arguments -d -a arg1=foo
arg2:
```

### Order of precedence of arguments
This is an order in which argument values are resolved:
1. If you provide argument using `-a`/`--arg` switch, it will always be used. You will not be prompted. Default value is ignored.
2. If you use `-d`/`--use-defaults` switch, dbgr will use default values when possible. You will not be prompted for arguments with default values.
3. You will get prompted for arguments without default values. Hitting enter without any input will result in empty string being used.
4. You will get prompted for arguments with default values. Hitting enter without any input will use default value.


## Return value
Your request can return a value. This return value will be printed to the terminal when you execute a request. It also gets returned when you implement [recursive calls](#recursive-calls). This can be usefull for example for authentication.

The return value also get cached when [cache is used](#caching).


## Environment
Environments offer you different way to specify variables for your requests. Your default environment is placed in `default.ini`. This is a file in ini format using [ExtendedInterpolation](https://docs.python.org/3/library/configparser.html#configparser.ExtendedInterpolation).

You can change the environment that will be used with `-e`/`--env` switch. DBGR searched for environments in current working directory in .ini files. Name of the environment is the name of the file without suffix.


## Recursive calls
Sometimes you might need to make a different requests before executing what you really want to do. For example to download user data, you need to login first. You can do that by using coroutine `dbgr.response`. It accepts at least 3 arguments - name of the request to execute as a string (you can specify module the same as in terminal), environment and session.

> In most cases you'll call another requests with the session and environment your function received. But you can also modify them before calling `response`.

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

> DBGR doens't try to detect reccursion. Be carefull not to unintentionaly cause DDoS on your (or some elses) servers.


### Arguments
As with the terminal execution, you can provide arguments for recursive calls. Simply add them as named arguments:

```
@request
async def login(env, session, username):
    rv = session.post('...login', data={'username': username})
    return await rv.json()

@request
async def get_comments(env, session):
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
    auth = response('list_comments', env, session, use_defaults=True)
```

> Order of precedence is the same as in terminal execution. You will still get promted for arguments witch don't have any value.


## Caching
You can mark request to be cached. All subsequent calls of the same request will be suspended and the result will be taken from cache. This is usefull for example when you work with API that requires sign-in. You usually want to call the authentication endpoint only once at the beginning and then just re-use cached value.

To enable caching call `@request` decorator with `cache` argument:

```
@request(cache='session')
async def login(env, session):
    ...
```

There is only one supported cache type at this moment: `session`. This type stores the result in memory for the time the program is running. This is not very usefull when you execute requests one by one. But in interactive mode, the value is cached until you terminate DBGR.

The cache key is constructed from the request and values of all arguments. If you call cached request with different arguments, it will get executed.

Cache stores only last used value. If you call call request with `cache=False` while you already have a result in cache, the request will get executed and new value will be stored in cache.

```
@request(cache='session')
async def login(env, session):
    ...

@request
async def list_comments(env, session):
    auth = response('login', env, session, cache=False) # This will result in HTTP call
    ...
```


## Asserts
DBGR supports assertions in requests. If a assert fails, it will get reported to the terminal.

```
@request
async def create_item(env, session):
    rv = session.post('/comments', data={...})
    assert rv.status == 201
```


## Autocomplete and History
DBGR supports autocomplete for commands and requests. You need to install and setup [argcomplete](https://pypi.org/project/argcomplete/) according to documentation.

Interactive mode supports terminal history.
