import os
from textwrap import dedent
from dbgr import environment
from tests.conftest import mock_file


def test_get_environments(monkeypatch):
    monkeypatch.setattr(
        environment.glob, 'glob', lambda _: ['/path/env1.ini', 'env2.ini']
    )
    assert environment.get_environments() == ['env1', 'env2']


def test_load_config(mock_file):
    mock_file('default.ini', dedent('''
        [section]
        key: value
    '''))
    env = environment.Environment('default')
    assert env['section']['key'] == 'value'


def test_load_empty_config_doesnt_fail(mock_file):
    mock_file('default.ini', '')
    env = environment.Environment('default')


def test_load_multiple_sections(mock_file):
    mock_file('default.ini', dedent('''
        [DEFAULT]
        default_key: default_value

        [section]
        key: value
    '''))
    env = environment.Environment('default')
    assert env['section']['key'] == 'value'
    assert env['DEFAULT']['default_key'] == 'default_value'


def test_default_section_not_in_sections(mock_file):
    mock_file('default.ini', dedent('''
        [DEFAULT]
        default_key: default_value

        [section]
        key: value
    '''))
    env = environment.Environment('default')
    assert env.sections() == ['section']


def test_interpolation(mock_file):
    mock_file('default.ini', dedent('''
        [DEFAULT]
        url: localhost
        sub_url: ${url}/sub_url

        [section]
        section_url: ${DEFAULT:url}/section_url
    '''))
    env = environment.Environment('default')
    assert env['DEFAULT']['sub_url'] == 'localhost/sub_url'
    assert env['section']['section_url'] == 'localhost/section_url'


def test_init_environment(mock_file):
    mock_file('not_default.ini', dedent('''
        [section]
        key: value
    '''))
    environment.init_environment('not_default')
    assert environment._ENVIRONMENT['section']['key'] == 'value'


def test_get_environment_creates_default_environment(mock_file):
    mock_file('default.ini', dedent('''
        [section]
        key: value
    '''))
    env = environment.get_environment()
    assert env['section']['key'] == 'value'


def test_get_environment_cached(mock_file):
    mock_file('default.ini', dedent('''
        [section]
        key: value
    '''))
    env1 = environment.get_environment()
    env2 = environment.get_environment()
    assert env1 == env2
