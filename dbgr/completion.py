from dbgr.requests import get_requests_list


class RequestsCompleter:
    def __init__(self):
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
        self.choices = tuple(options.union(uniques))

    def __call__(self, **kwargs):
        return self.choices


class ModulesCompleter:
    def __init__(self):
        self.choices = (r.__module__ for r in get_requests_list())

    def __call__(self, **kwargs):
        return self.choices
