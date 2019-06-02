import colorama


class Argument:
    def __init__(self, name, annotation):
        self.name = name
        self.annotation = annotation

    def __str__(self):
        if self.annotation:
            return f'{self.name} [type: {self.annotation}]'
        return self.name

    def cast(self, value):
        try:
            return self.annotation.cast(value)
        except:
            print(f'{colorama.Fore.RED}String "{value}" cannot be converted to {self.annotation}')
            raise

    def value_input(self, nullable=False):
        value = self.annotation.value_input(self)
        if nullable and value == '':
            return None
        try:
            return self.cast(value)
        except ValueError:
            return self.value_input(nullable)


class NoDefaultValueArgument(Argument):
    def get_value(self, kwargs, use_default=None): # pylint: disable=W0613
        if self.name in kwargs:
            return self.cast(kwargs[self.name])
        return self.value_input()


class DefaultValueArgument(Argument):
    def __init__(self, name, annotation, value):
        super().__init__(name, annotation)
        self.value = value

    def __str__(self):
        buffer = f'{self.name} [default: {self.annotation.repr_value(self.value)}'
        if self.annotation:
            return f'{buffer}, type: {self.annotation}]'
        return f'{buffer}]'

    def get_value(self, kwargs, use_default=False):
        if self.name in kwargs:
            value = self.cast(kwargs[self.name])
        elif use_default:
            value = self.value
        else:
            value = self.value_input(nullable=True)
            if value is None:
                value = self.value
        return value
