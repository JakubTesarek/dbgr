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

Now you have 2 options how to install dbgr.

### Install with pip
You can install dbgr from local directory by running this command from the source directory:

```
$ source p3.7/bin/activate
(p3.7) $ pip install -e .
```

This will automatically create `dbgr` command so you run `dbgr --version` straight away. Unfortunately, every time you make a change to dbgr source code, you will need to run `pip install -e .` again to re-install it.

### Create alias function
Other option is to not install DBGR at all and instead add this to your `.bash_profile`:

```
dbgr() {
    . <path_to_dbgr>/p3.7/bin/activate
    eval "$(register-python-argcomplete dbgr)"
    <path_to_dbgr>/app.py $@
    deactivate
}
```

This will create new function that will activate the Python environment, register autocompleter and run `dbgr/app.py` when you call it.


## Tooling
The file `Makefile` contains multiple commands that can be usefull when developing DBGR. Run `make` to see all the available commands.


## Testing
To run all unit-tests, simply `make test`.

> `make test` also measures code coverage and fails when it's not 100%. This is done to remind me of the end goal to achieve 100% code test coverage. You can ignore it for now. Just make sure that all new changes are covered and overall coverage is raising.


## Linting
DBGR user pylint with some lints disabled. See `.pylintrc` for details. You can execute linter by running `make lint`. Score of 10.0 is required for all changes.
