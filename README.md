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

## Endpoints
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
Environments enable you to define variables, eg. different urls, and then run your requests with different arguments. Your default environment is placed in `default.ini`. This is a file in ini format using (ExtendedInterpolation)[https://docs.python.org/3/library/configparser.html#configparser.ExtendedInterpolation].

## Autocomplete
DBGR supports autocomplete for commands and requests. You need to install and setup (argcomplete)[https://pypi.org/project/argcomplete/] according to documentation.
