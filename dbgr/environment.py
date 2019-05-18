import os
import re
from configparser import ConfigParser, ExtendedInterpolation


class Environment(ConfigParser):
    def __init__(self, env_name, session):
        super().__init__(interpolation=ExtendedInterpolation())
        self.session = session
        self.read(f'{env_name}.ini')
