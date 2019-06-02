import getpass


class Type:
    supported_types = ['bool', 'str', 'int', 'float']

    def __init__(self, cls):
        self.cls = None
        if cls and cls.__name__ in self.supported_types:
            self.cls = cls

    def cast(self, value):
        if value is not None and self:
            if self.cls == bool:
                if isinstance(value, str):
                    value = value.lower()
                return value not in [0, 0.0, '0', False, 'f', 'false', 'n', 'no']
            return self.cls(value)
        return value

    def __str__(self):
        if self:
            return self.cls.__name__
        return ''

    def __bool__(self):
        return self.cls is not None

    def value_input(self, prompt):
        return input(f'{prompt}: ')

    def repr_value(self, value):
        try:
            return str(self.cast(value))
        except ValueError:
            return str(value)

    @staticmethod
    def get_type(annotation):
        if annotation is not None and issubclass(annotation, Type):
            return annotation()
        return Type(annotation)


class SecretType(Type):
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
