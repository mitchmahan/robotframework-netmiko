from os import path
import pathlib
from robot.api import logger as robot_logger
import json
from jinja2 import Environment, FileSystemLoader


class HtmlLogger():
    """ Build HTML strings to use for logging content inside Robot Framework
    test cases.

    Uses Jinja2 templates stored in templates/
    """

    def __init__(self):
        curdir = pathlib.Path(__file__).parent.absolute()
        templates = path.join(curdir, 'templates')
        # Setup Jinja to look in the correct folder for templates
        self.env = Environment(
            loader=FileSystemLoader(searchpath=templates),
            trim_blocks=True,
            lstrip_blocks=True
        )
        with open(path.join(templates, 'style.css')) as f:
            css = f.read()
        self.style = f"<style type='text/css'>{css}</style>"

    def cli(self, host: str, command: str, output: str) -> str:
        """ Use Jinja2 to create an HTML log for RobotFramework output.

        Args:

        Returns:
            msg (str):
        """
        j2_vars = {
            'host': host,
            'command': command,
            'output': output
        }
        template = self.env.get_template('cli.j2')
        msg = template.render(**j2_vars)
        self.info(msg)

    def cli_parse(self, host: str, command: str, output: str, ttp_template: str, _vars) -> str:
        """ Use Jinja2 to create an HTML log for RobotFramework output.

        Args:

        Returns:
            msg (str):
        """
        j2_vars = {
            'command': command,
            'output': output,
            'ttp_template': ttp_template,
            '_vars': json.dumps(_vars, indent=4)
        }
        template = self.env.get_template('cli_parse.j2')
        msg = template.render(**j2_vars)
        self.info(msg)

    def info(self, msg):
        robot_logger.info(self.style + msg, html=True)
