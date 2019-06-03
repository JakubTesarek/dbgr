import pytest
from argparse import Namespace
from dbgr import meta
from tests.conftest import escape_ansi
from dbgr.commands import (
    argument_parser, interactive_command, request_command, list_command,
    environments_command, version_command
)


@pytest.mark.parametrize('args', [
    ['-v'], ['--version']
])
def test_version_command(args):
    res = argument_parser().parse_args(args)
    assert isinstance(res, Namespace)
    assert res.version == True


@pytest.mark.parametrize('args', [
    ['-v'], ['--version']
])
def test_version_command(args):
    res = argument_parser().parse_args(args)
    assert isinstance(res, Namespace)
    assert res.version == True


@pytest.mark.parametrize('args, namespace', [
    (['i'], {'use_defaults': False, 'env': 'default'}),
    (['interactive'], {'use_defaults': False, 'env': 'default'}),
    (['int'], {'use_defaults': False, 'env': 'default'}),
    (['i', '-d'], {'use_defaults': True, 'env': 'default'}),
    (['i', '--use-defaults'], {'use_defaults': True, 'env': 'default'}),
    (['i', '-e', 'test'], {'use_defaults': False, 'env': 'test'}),
    (['i', '--env', 'test'], {'use_defaults': False, 'env': 'test'}),
    (['i', '--env', 'test', '-d'], {'use_defaults': True, 'env': 'test'})
])
def test_interactive_command(args, namespace):
    res = argument_parser().parse_args(args)
    assert isinstance(res, Namespace)
    assert res.func == interactive_command
    for key, value in namespace.items():
        assert getattr(res, key) == value


@pytest.mark.parametrize('args, namespace', [
    (['r', 'test'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'default',
        'arguments': []
    }),
    (['req', 'test'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'default',
        'arguments': []
    }),
    (['request', 'test'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'default',
        'arguments': []
    }),
    (['request', 'test', '-d'], {
        'request': 'test',
        'use_defaults': True,
        'env': 'default',
        'arguments': []
    }),
    (['request', 'test', '--use-defaults'], {
        'request': 'test',
        'use_defaults': True,
        'env': 'default',
        'arguments': []
    }),
    (['request', 'test', '-e', 'test2'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'test2',
        'arguments': []
    }),
    (['request', 'test', '--env', 'test2'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'test2',
        'arguments': []
    }),
    (['request', 'test', '-a', 'x=1', '-a', 'y=2'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'default',
        'arguments': ['x=1', 'y=2']
    }),
    (['request', 'test', '--arg', 'x=1', '--arg', 'y=2'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'default',
        'arguments': ['x=1', 'y=2']
    }),
    (['request', 'test', '--use-defaults', '-a', 'x=1', '-a', 'y=2'], {
        'request': 'test',
        'use_defaults': True,
        'env': 'default',
        'arguments': ['x=1', 'y=2']
    }),
    (['request', 'test', '-e', 'test2', '-a', 'x=1', '-a', 'y=2'], {
        'request': 'test',
        'use_defaults': False,
        'env': 'test2',
        'arguments': ['x=1', 'y=2']
    })
])
def test_request_command(args, namespace):
    res = argument_parser().parse_args(args)
    assert isinstance(res, Namespace)
    assert res.func == request_command
    for key, value in namespace.items():
        assert getattr(res, key) == value


@pytest.mark.parametrize('args, namespace', [
    (['l'], {'module': None}),
    (['list'], {'module': None}),
    (['list', 'module'], {'module': 'module'}),
    (['list', 'module:request'], {'module': 'module:request'}),
    (['list', ':request'], {'module': ':request'})
])
def test_list_command(args, namespace):
    res = argument_parser().parse_args(args)
    assert isinstance(res, Namespace)
    assert res.func == list_command
    for key, value in namespace.items():
        assert getattr(res, key) == value


@pytest.mark.parametrize('args', [
    ['e'], ['envs'], ['list-environments']
])
def test_environments_command(args):
    res = argument_parser().parse_args(args)
    assert isinstance(res, Namespace)
    assert res.func == environments_command


def test_version_command(capsys):
    version_command()
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == f'{meta.__version__}\n'

