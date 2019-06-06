import getpass
import dateparser
from datetime import datetime, time, date


class Type:
    def cast(self, value):
        return value

    def __str__(self):
        return ''

    def __bool__(self):
        return False

    def value_input(self, prompt):
        return input(f'{prompt}: ')

    def repr_value(self, value):
        try:
            return str(self.cast(value))
        except ValueError:
            return str(value)

    @staticmethod
    def get_type(annotation):
        if annotation is not None:
            if issubclass(annotation, Type):
                return annotation()
            if annotation == bool:
                return BooleanType()
            if annotation == datetime:
                return DatetimeType()
            if annotation == time:
                return TimeType()
            if annotation == date:
                return DateType()
            if annotation in PrimitiveType.supported_types:
                return PrimitiveType(annotation)
        return Type()


class BooleanType(Type):
    def cast(self, value):
        if isinstance(value, str):
            value = value.lower()
        if value in [0, 0.0, '0', False, 'f', 'false', 'n', 'no']:
            return False
        return bool(value)

    def __str__(self):
        return 'bool'

    def __bool__(self):
        return True


class PrimitiveType(Type):
    supported_types = [str, int, float]

    def __init__(self, cls):
        if cls not in self.supported_types:
            raise TypeError(f'Type "{cls}" is not supported primitive type')
        self.cls = cls

    def cast(self, value):
        if value is not None:
            return self.cls(value)

    def __str__(self):
        return self.cls.__name__

    def __bool__(self):
        return True


class SecretType(PrimitiveType):
    def __init__(self):
        super().__init__(str)

    def value_input(self, prompt):
        return getpass.getpass(f'{prompt}: ')

    def __str__(self):
        return 'secret'

    def repr_value(self, value):
        value = super().repr_value(value)
        length = len(value)
        if length <= 5:
            return '*' * length
        return f'{value[0]}{"*" * (length - 2)}{value[-1]}'

    def __bool__(self):
        return True


class DatetimeType(Type):
    def cast(self, value):
        if isinstance(value, datetime):
            return value
        if value is not None:
            if isinstance(value, time):
                value = datetime.combine(datetime.today(), value)
            if isinstance(value, date):
                value = datetime.combine(value, datetime.now().time())
            if isinstance(value, str):
                value = dateparser.parse(value)
            if not value:
                raise ValueError(f'{type(value)} "{value}" cannot be converted to {self}')
            return value

    def __str__(self):
        return 'datetime'

    def __bool__(self):
        return True

    def repr_value(self, value):
        casted = super().repr_value(value)
        if isinstance(value, str):
            return f'{value} ({casted})'
        return casted


class DateType(DatetimeType):
    def cast(self, value):
        value = super().cast(value)
        if value is not None:
            return value.date()

    def __str__(self):
        return 'date'


class TimeType(DatetimeType):
    def cast(self, value):
        value = super().cast(value)
        if value is not None:
            return value.time()

    def __str__(self):
        return 'time'
