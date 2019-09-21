from dbgr.types import Type


class Result:
    def __init__(self, value, annotation=None, cached=False):
        self._value = value
        self.cached = cached
        if annotation is None:
            annotation = Type()
        self.annotation = annotation

    def __str__(self):
        return self.annotation.repr_value(self.value)

    @property
    def value(self):
        return self.annotation.cast(self._value)
