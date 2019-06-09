# Contributors
Thank your contribution to DBGR. Any help or feedback is greatly appreciated.

## Development setup
If you want to develop debugger locally, there is alternative installation process that will make this experience easier.

First, [create a fork of DBGR](https://help.github.com/en/articles/fork-a-repo).
Then you can clone the forked repo and create local environment:
```
$ git clone https://github.com/<your_username>/dbgr
$ cd dbgr
$ virtualenv p3.7 --python=python3.7
$ source p3.7/bin/activate
(p3.7) $ pip install -r requirements.txt -r requirements-dev.py
```

> The process for setting up python 3.6 is the same.


Now you can install DBGR from local directory:

```
$ source p3.7/bin/activate
(p3.7) $ pip install -e .
```


## Testing
`make test`
> The file `Makefile` contains multiple commands that can be usefull when developing DBGR. Run `make` to see all the available commands.

`make test` also measures code coverage and fails when it's not 100%. This is done to remind me of the end goal to achieve 100% code test coverage. You can ignore it for now. Just make sure that all new changes are covered and overall coverage is raising.


## Linting
`make lint`
DBGR user pylint with some lints disabled. See `.pylintrc` for details. Score of 10.0 is required for all changes.


## Links
* [Travis-io build job](https://travis-ci.org/JakubTesarek/dbgr)
* [Codev test coverage statistics](https://codecov.io/gh/JakubTesarek/dbgr)
