from dbgr import environment


def test_get_environments(monkeypatch):
    monkeypatch.setattr(
        environment.glob, 'glob', lambda _: ['/path/env1.ini', 'env2.ini']
    )
    assert environment.get_environments() == ['env1', 'env2']
