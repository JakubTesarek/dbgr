import os
import re
from configparser import ConfigParser, ExtendedInterpolation


class Environment(ConfigParser):
    def __init__(self, env_name):
        super().__init__(interpolation=ExtendedInterpolation())
        self.read(f'{env_name}.ini')
