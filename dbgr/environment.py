import os
import glob
from configparser import ConfigParser, ExtendedInterpolation

_ENVIRONMENT = None
DEFAULT_ENVIRONMENT = 'default'

def get_environments():
    environments = []
    for env_file in glob.glob(f'{os.getcwd()}/*.ini'):
        environments.append(os.path.splitext(os.path.basename(env_file))[0])
    return environments


class Environment(ConfigParser):
    def __init__(self, env_name):
        super().__init__(interpolation=ExtendedInterpolation())
        self.read(f'{env_name}.ini')


def init_environment(path=DEFAULT_ENVIRONMENT):
    global _ENVIRONMENT # pylint: disable=W0603
    _ENVIRONMENT = Environment(path)


def get_environment():
    global _ENVIRONMENT # pylint: disable=W0603
    if not _ENVIRONMENT:
        init_environment()
    return _ENVIRONMENT
