import os
import re
import glob
from configparser import ConfigParser, ExtendedInterpolation


def get_environments():
    environments = []
    for f in glob.glob(f'{os.getcwd()}/*.ini'):
        environments.append(os.path.splitext(os.path.basename(f))[0])
    return environments


class Environment(ConfigParser):
    def __init__(self, env_name):
        super().__init__(interpolation=ExtendedInterpolation())
        self.read(f'{env_name}.ini')
