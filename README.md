[![PyPI version](https://badge.fury.io/py/dbgr.svg)](https://badge.fury.io/py/dbgr)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build Status](https://travis-ci.org/JakubTesarek/dbgr.svg?branch=master)](https://travis-ci.org/JakubTesarek/dbgr)
[![codecov](https://codecov.io/gh/JakubTesarek/dbgr/branch/master/graph/badge.svg)](https://codecov.io/gh/JakubTesarek/dbgr)

# DBGR
Dbgr [read 'ˌdiːˈbʌɡər'] is a interactive terminal tool to test and debug HTTP APIs. It offers alternative to [Postman](https://www.getpostman.com/), [Insomnia](https://insomnia.rest/) and other HTTP clients.

* DBGR allows gives you full control over your requests
* You can programatically process the responses
* You don't have to leave terminal when working with APIs
* Document your API with code


## Content
* [Installation and dependencies](#installation-and-dependencies)
  * [Development setup](#development-setup)
* [Project setup](#project-setup)
* [Requests](#requests)
  * [Names](#names)
  * [Listing requests](#listing-requests)
* [Arguments](#arguments)
  * [Order of precedence of arguments](#order-of-precedence-of-arguments)
  * [Types annotations](#types-annotations)
    * [Boolean type](#boolean-type)
    * [Secret type](#secret-type)
* [Return value](#return-value)
  * [Secret return value](#secret-return-value)
* [Environment](#environment)
* [Recursive calls](#recursive-calls)
  * [Arguments](#arguments-1)
* [Caching](#caching)
* [Asserts](#asserts)
* [Autocomplete and History](#autocomplete-and-history)


## Installation and dependencies
The easiest way to install DBGR is via [pypi](https://pypi.org/project/dbgr/).

```
pip install dbgr
```

DBGR requires Python 3.7. Also, if you want to use terminal autocompletion, you need appropriet bash version or [setup your shell](#autocomplete_and_history).

> For alternative ways of installation, see [CONTRIBUTORS.md](CONTRIBUTORS.md).


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
DBGR request is a function decorated with `@dbgr.request`. In its simplest form it accepts two arguments. First argument is the environment it was executed in. The second argument is an instance of `aiohttp.ClientSession`. You don't have to return or log anything from your request. The ClientSession does all logging automatically.

### Names
By default you execute your request with `$ dbgr r <function_name>`. Optionally you can change the name of the request with an argument:

```
@requst(name='different_name')
async def get_example(env, session):
    await session.get('http://example.com')
```

And then you'll execute it with its alternative name `$ dbgr r different_name`.

> Name of a request can contain only letters, numbers and/or underscores. Names are case sensitive.

DBGR automatically loads requests from all .py files in working directory. This can lead to collisions in names. Therefore you can execute the endpoint with fully qualified name including module name: `$ dbgr r module:function`. Module name is simply the name of the file without extension.

### Listing requests
DBGR has a command to list all registered commnads: `dbgr list-requests` or `dbgr l`. It accepts optional argument with module name: `dbgr l placeholder`. If you use it, DBGR will list only request from that module. If you only want to see details of one request, you can also use fully qualified request name `dbgr l placeholder:post`.

If you are looking for a request but you don't know which module it's in, you can omit the module name and just prefix the request with `:`, like this: `dbgr l :users`. DBGR will then list all requests named `users` from all modules.

```
$ dbgr list-requests :users
placeholder:
 - users
   Retrieve all users
github:
 - users
   List all user that have access to my repository
```

## Arguments
When defining your request, you can specify any number of arguments that it will accept (besides env and session). These arguments will be filled with values specified when you call your request. If you don't provide them in the terminal, DBGR will prompt you for value. You can also define default values for some or all arguments.

```
@request
async def many_arguments(env, session, arg1, arg2, arg3='foo'):
    pass
```

When you call this request from terminal, you will be prompted for all 3 arguments. For `arg3` you will be offered to use default value:

```
$ dbgr r many_arguments
arg1:
arg2:
arg3 [default: foo]:
```

You can provide values when you execute your request with `-a` or `--arg`:

```
$ dbgr r many_arguments -a arg1=foo
arg2:
arg3 [default: foo]:
```

```
$ dbgr r many_arguments -a arg1=foo -a arg3=bar
arg2:
```

Arguments mentioned in command without value are assumed to be flags and will be resolved to `True`:

```
$ dbgr r request -a arg1 # arg1 == True
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

### Types annotations
It is possible to annotate expected types of arguments in the request definition. DBGR will try to convert the input value into desired type.

You can annotate as many arguments as you want. Arguments without annotation will be passed as strings.

```
@request
async def get_comment(env, session, comment_id: int):
    data = session.get('/comments', params={'id': comment_id})
```

```
$dbgr r get_comment
comment_id [type: int]: # Input will be converted to integer
```

You can also combine default values with annotation.

```
@request
async def get_comment(env, session, comment_id: int=1):
    data = session.get('/comments', params={'id': comment_id})
```

```
$dbgr r get_comment
comment_id [default: 1, type: int]:
```

If you use default value by pressing enter without any input, DBGR will not check type and will just pass the value as it is.

DBGR currently supports these type: `int`, `float`, `bool`, `str`. Every other annotation type will be ignored.

#### Boolean type
Booleans are handled in a special way. Values `0`, `f`, `false`, `n`, `no` (and their variants in different case) will be converted to `False`, everything else will be converted to `True`.

#### Secret type
Requests can also prompt you for password. For that, use type `secret` from `dbgr` module:

```
from dbgr import request, secret

@request
async def login(env, session, username, password: secret):
    await session.post('/login', data={'username': username, 'password': password})
```

DBGR will display password prompt for each field of type `secret`:

```
$ dbgr r login
username: jakub@tesarek.me
password [type: secret]: #will show nothing
```

Secret type can have default value too, just like any other argument. In terminal, it will be displayed obfuscated:
```
from dbgr import request, secret

@request
async def change_password(env, session, password: secret='SuperSecret'):
    await session.post('/change_password', data={'password': password})
```

```
$ dbgr r change_password
password [default: S*********t, type: secret]:
```


## Return value
Your request can return a value. This return value will be printed to the terminal when you execute a request. It also gets returned when you implement [recursive calls](#recursive-calls). This can be useful for example for authentication.

The return value also get cached when [cache is used](#caching).

You can use type hinting with the same [limitations as with arguments](#types_annotations). DBGR will try to convert the return value into the specified type.

```
@request
async def count_comments(env, session) -> int:
    resp = session.get('/comments')
    return len(resp.json())
```

### Secret return value
If your request returns [Secret Type](#secret-type), it will be obfuscated in the terminal output:

```
from dbgr import request, secret

@request
async def retrieve_password(env, session) -> secret:
    res = await session.get('/get_password')
    return await res.text()
```

```
$ dbgr r retrieve password
# request output
Result (secret): S*******d
```

> **The secret information will still show in the request log if it's send as plaintext.**

## Environment
Environments offer you different way to specify variables for your requests. Your default environment is placed in `default.ini`. This is a file in ini format using [ExtendedInterpolation](https://docs.python.org/3/library/configparser.html#configparser.ExtendedInterpolation).

You can change the environment that will be used with `-e`/`--env` switch. DBGR searched for environments in current working directory in .ini files. Name of the environment is the name of the file without suffix.


## Recursive calls
Sometimes you might need to make a different request before executing what you really want to do. For example to download user data, you need to login first. You can do that by using coroutine `dbgr.response`. It accepts at least 3 arguments - name of the request to execute as a string (you can specify module the same as in terminal), environment and session.

> In most cases you'll call another requests with the session and environment your function received. But you can also modify them before calling `response`.

```
from dbgr import request, response

@request
async def login(env, session):
    rv = session.post('/login', data={'username': env['login']})
    return await rv.json()

@request
async def get_comments(env, session):
    auth = response('login', env, session)
    data = session.get('/comments', headers={'Authorization': f'Bearer {auth["token"}'})
```

> DBGR doens't detect reccursion. Be carefull not to unintentionaly cause DDoS on your (or some elses) servers.


### Arguments
As with the terminal execution, you can provide arguments for recursive calls. Simply add them as named arguments:

```
@request
async def login(env, session, username):
    rv = session.post('/login', data={'username': username})
    return await rv.json()

@request
async def get_comments(env, session):
    auth = response('login', env, session, username='admin@example.com')
    data = session.get('/comments', headers={'Authorization': f'Bearer {auth["token"}'})
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

> Order of precedence is the same as in terminal execution. You will still get promted for arguments which don't have any value.


## Caching
You can mark request to be cached. All subsequent calls of the same request will be suspended and the result will be taken from cache. This is useful for example when you work with API that requires sign-in. You usually want to call the authentication endpoint only once at the beginning and then just re-use cached value.

To enable caching call `@request` decorator with `cache` argument:

```
@request(cache='session')
async def login(env, session):
    ...
```

There is only one supported cache type at this moment: `session`. This type stores the result in memory for the time the program is running. This is not very useful when you execute requests one by one. But in interactive mode, the value is cached until you terminate DBGR.

The cache key is constructed from the request and values of all arguments. If you call cached request with different arguments, it will get executed.

Cache stores only last used value. If you call request with `cache=False` while you already have a result in cache, the request will get executed and new value will be stored in cache.

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
DBGR supports assertions in requests. If an assert fails, it will get reported to the terminal.

```
@request
async def create_item(env, session):
    rv = session.post('/comments', data={...})
    assert rv.status == 201
```


## Autocomplete and History
DBGR supports autocomplete for commands and requests. You need to install and setup [argcomplete](https://pypi.org/project/argcomplete/) according to documentation.

Interactive mode supports terminal history.
