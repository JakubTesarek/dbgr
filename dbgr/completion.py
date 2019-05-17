from dbgr.requests import get_requests_list


class Completer:
    def __init__(self):
        self.choices = None
    
    def __call__(self, **kwargs):
        if not self.choices:
            self.choices = self.get_choices()
        return self.choices

    def get_choices(self):
        raise NotImplementedError(f'{__name__} needs to implemented in subclass')
    

class RequestsCompleter(Completer):
    def get_choices(self):
        uniques = set()
        duplicates = set()
        options = set()
        for r in get_requests_list():
            options.add(f'{r.__module__}:{r.__name__}')
            if r.__name__ not in duplicates:
                if r.__name__ in uniques:
                    duplicates.add(r.__name__)
                    uniques.remove(r.__name__)
                else:
                    uniques.add(r.__name__)
        return tuple(options.union(uniques))


class ModulesCompleter(Completer):
    def get_choices(self):
        return (r.__module__ for r in get_requests_list())
