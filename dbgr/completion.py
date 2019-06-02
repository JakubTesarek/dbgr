from dbgr.requests import get_requests
from dbgr.environment import get_environments


class Completer:
    def __init__(self):
        self.choices = None

    def __call__(self, **kwargs):
        if not self.choices:
            self.choices = self.get_choices()
        return self.choices

    def get_choices(self):
        raise NotImplementedError(f'"{__name__}" needs to be implemented in subclass')


class EnvironmentsCompleter(Completer):
    def get_choices(self):
        return tuple(get_environments())


class RequestsCompleter(Completer):
    def get_choices(self):
        uniques, duplicates, options = set(), set(), set()
        for module, requests in get_requests().items():
            for name in requests.keys():
                options.add(f'{module}:{name}')
                if name not in duplicates:
                    if name in uniques:
                        duplicates.add(name)
                        uniques.remove(name)
                    else:
                        uniques.add(name)
        return tuple(options.union(uniques))


class ModulesCompleter(Completer):
    def get_choices(self):
        return tuple(get_requests().keys())
