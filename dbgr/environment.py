import os
import jinja2
from configparser import ConfigParser, ExtendedInterpolation

class Environment():
    def __init__(self, template_file):
        self.env_dir = f'{os.getcwd()}'
        self.load_template(template_file)

    def load_template(self, template_file):
        templateLoader = jinja2.FileSystemLoader(searchpath=self.env_dir)
        templateEnv = jinja2.Environment(loader=templateLoader)
        self.template = templateEnv.get_template(template_file)

    @property
    def env(self):
        conf_template = self.template.render()
        conf = ConfigParser(interpolation=ExtendedInterpolation())
        conf.read_string(conf_template)
        return conf
