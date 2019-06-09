from pprint import pformat
import colorama
from dbgr.types import Type


class Result:
    def __init__(self, value, annotation=None, cached=False):
        self._value = value
        self.cached = cached
        if annotation is None:
            annotation = Type()
        self.annotation = annotation

    def __str__(self):
        from_cache = ''
        if self.cached:
            from_cache = ', from cache'
        buffer = (
            f'{colorama.Style.BRIGHT}Result{colorama.Style.RESET_ALL} '
            f'{colorama.Style.DIM}({type(self.value).__name__}{from_cache})'
        )
        if self.value is not None:
            buffer += (
                f'{colorama.Style.RESET_ALL}:\n'
                f'{pformat(self.annotation.repr_value(self.value))}'
            )
        return buffer

    @property
    def value(self):
        return self.annotation.cast(self._value)
