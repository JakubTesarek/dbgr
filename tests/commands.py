import pytest
from argparse import Namespace
from dbgr import meta
from tests.conftest import escape_ansi, attrdict, mock_request
from dbgr import commands
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


@pytest.mark.asyncio
async def test_environments_command_list_environments(capsys, monkeypatch):
    monkeypatch.setattr(commands, 'get_environments', lambda: ['default', 'another'])
    await environments_command(attrdict({'environment': None}))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '- default\n- another\n'


@pytest.mark.asyncio
async def test_environments_command_list_environment_variables(capsys, monkeypatch):
    class MockedEnvironment:
        def __init__(self, env):
            self.data = {
                'section1': [
                    ('attr1', 'value1'),
                    ('attr2', 'value2')
                ],
                'section2': [
                    ('attr1', 'value1')
                ]
            }

        def items(self, section):
            return self.data[section]

        def sections(self):
            return self.data.keys()


    monkeypatch.setattr(commands, 'Environment', MockedEnvironment)
    await environments_command(attrdict({'environment': 'default'}))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''section1
- attr1: value1
- attr2: value2
section2
- attr1: value1
'''


@pytest.mark.asyncio
async def test_interactive_command(capsys, monkeypatch):
    async def mocked_prepare_execute(req, arg):
        print(req)

    inputs = ['req1', 'req2', '\x03']
    def mocked_input(prompt):
        i = inputs.pop(0)
        if i == '\x03':
            raise SystemExit()
        return i

    monkeypatch.setattr('builtins.input', mocked_input)
    monkeypatch.setattr(commands, 'prepare_and_execute_request', mocked_prepare_execute)
    with pytest.raises(SystemExit):
        await interactive_command({})
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''Dbgr interactive mode; press ^C to exit.
req1
req2
'''


@pytest.mark.asyncio
async def test_list_command_all(monkeypatch, capsys):
    requests = {
        'module1': {
            'req1': mock_request(name='req1', module='module1'),
            'req2': mock_request(name='req2', module='module1')
        },
        'module2': {
            'req1': mock_request(name='req1', module='module2'),
            'req3': mock_request(name='req3', module='module2')
        }
    }
    monkeypatch.setattr(commands, 'get_requests', lambda: requests)
    await list_command(attrdict({'module': None}))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''module1:
 - req1
 - req2
module2:
 - req1
 - req3
'''


@pytest.mark.asyncio
async def test_list_command_filter_module(monkeypatch, capsys):
    requests = {
        'module1': {
            'req1': mock_request(name='req1', module='module1'),
            'req2': mock_request(name='req2', module='module1')
        },
        'module2': {
            'req1': mock_request(name='req1', module='module2'),
            'req3': mock_request(name='req3', module='module2')
        }
    }
    monkeypatch.setattr(commands, 'get_requests', lambda: requests)
    await list_command(attrdict({'module': 'module1'}))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''module1:
 - req1
 - req2
'''



@pytest.mark.asyncio
async def test_list_command_filter_module_request(monkeypatch, capsys):
    requests = {
        'module1': {
            'req1': mock_request(name='req1', module='module1'),
            'req2': mock_request(name='req2', module='module1')
        },
        'module2': {
            'req1': mock_request(name='req1', module='module2'),
            'req3': mock_request(name='req3', module='module2')
        }
    }
    monkeypatch.setattr(commands, 'get_requests', lambda: requests)
    await list_command(attrdict({'module': 'module1:req1'}))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''module1:
 - req1
'''


@pytest.mark.asyncio
async def test_list_command_request(monkeypatch, capsys):
    requests = {
        'module1': {
            'req1': mock_request(name='req1', module='module1'),
            'req2': mock_request(name='req2', module='module1')
        },
        'module2': {
            'req1': mock_request(name='req1', module='module2'),
            'req3': mock_request(name='req3', module='module2')
        }
    }
    monkeypatch.setattr(commands, 'get_requests', lambda: requests)
    await list_command(attrdict({'module': ':req1'}))
    captured = capsys.readouterr()
    assert escape_ansi(captured.out) == '''module1:
 - req1
module2:
 - req1
'''
