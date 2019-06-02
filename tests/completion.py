import pytest
from dbgr import completion

def test_completer_is_abstract():
    com = completion.Completer()
    with pytest.raises(NotImplementedError):
        com.get_choices()


def test_completer_caches():
    class MockedCompleter(completion.Completer):
        def __init__(self):
            super().__init__()
            self.call_count = 0

        def get_choices(self):
            self.call_count += 1
            return ('choice1', 'choice2')

    com = MockedCompleter()
    assert com() == ('choice1', 'choice2')
    assert com() == ('choice1', 'choice2')
    assert com.call_count == 1


def test_environments_completer(monkeypatch):
    monkeypatch.setattr(completion, 'get_environments', lambda: ['env1', 'env2'])
    com = completion.EnvironmentsCompleter()
    assert com() == ('env1', 'env2')


def test_requests_completer(monkeypatch, mocked_request):
    requests = {
        'module1': {
            'request1': mocked_request,
            'request2': mocked_request
        },
        'module2': {
            'request2': mocked_request,
            'request3': mocked_request
        },
        'module3': {
            'request2': mocked_request,
        }
    }
    monkeypatch.setattr(completion, 'get_requests', lambda: requests)
    com = completion.RequestsCompleter()
    assert set(com()) == set([
        'module1:request1', 'module1:request2', 'request1',
        'module2:request2', 'module2:request3', 'request3',
        'module3:request2'
    ])


def test_modules_completed(monkeypatch, mocked_request):
    requests = {
        'module1': {
            'request1': mocked_request,
        },
        'module2': {
            'request2': mocked_request,
        },
        'module3': {
            'request3': mocked_request,
        }
    }
    monkeypatch.setattr(completion, 'get_requests', lambda: requests)
    com = completion.ModulesCompleter()
    assert com() == ('module1', 'module2', 'module3')
