import os
import json
import jinja2

class Configuration():
    def __init__(self, template_file):
        self.template_dir = f'{os.getcwd()}/env'
        self.load_template(template_file)

    def load_template(self, template_file):
        templateLoader = jinja2.FileSystemLoader(searchpath=self.template_dir)
        templateEnv = jinja2.Environment(loader=templateLoader)
        self.template = templateEnv.get_template(template_file)

    @property
    def conf(self):
        conf_json = self.template.render()
        return json.loads(conf_json)