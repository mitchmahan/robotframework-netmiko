from os import path

try:
    # Optional Libraies
    from ttp import ttp
except ImportError:
    print(
        "You can install ttp if you plan to use ttp features."
    )

import json
import yaml
from jinja2 import Environment, FileSystemLoader
from robot.api import logger
import netmiko

from .errors import (
    NetmikoError,
    NetmikoConnectionError,
    ParserException,
    NetmikoTimeout,
)
from .connection_cache import NetmikoConnectionCache
from .loggers import HtmlLogger


class NetmikoLibrary:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_AUTO_KEYWORDS = True

    def __init__(self):
        if not hasattr(self.__class__, "_CONNECTIONS"):
            self.__class__._CONNECTIONS = NetmikoConnectionCache()

        # Default system that use use commit
        self.commit_os = ["cisco_xr", "junos"]

        # An HTML logger to make CLI interactions prettier in robot log
        self.loghtml = HtmlLogger()

    def __del__(self):
        if hasattr(self.__class__, "_CONNECTIONS"):
            self.__class__._CONNECTIONS.close_all()

    def open_connection(
        self,
        alias,
        ip,
        os,
        username,
        password,
        timeout=120,
        verbose=True,
        session_log=None,
        port=22
    ):
        """Open a new Netmiko connection and store it in the connection cache
        so we can switch between different netmiko connections.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Keywords ***
                Setup Connections
                    Open Connection     ${alias}   ${ip}    ${os}   ${usernmae}   ${password}

        Sets:
            index_or_alias (str):
                Alias for connection in the connection cache.

        Returns:
            netmiko.ConnectHandler (obj):
                A netmiko connection handler object.
        """
        device_profile = {
            "device_type": os,
            "username": username,
            "password": password,
            "ip": ip,
            "verbose": verbose,
            "global_delay_factor": 1,
            "timeout": timeout,
            "session_log": session_log,
            "port": port
        }
        self.ip = ip
        try:
            self.handler = netmiko.ConnectHandler(**device_profile)
            
            # Save the initial prompt for logging
            self.handler.initial_prompt = self.handler.find_prompt()

            index = self.__class__._CONNECTIONS.register(self.handler, alias=alias)
            logger.info("Registered new netmiko connection.")
            logger.info(f"Alias: {alias} Index: {index}")
        except ConnectionError:
            raise NetmikoConnectionError(f"Unable to connect to device [{ip}].")
        except TimeoutError:
            raise NetmikoTimeout(f"Timed out connecting to device {ip}.")

        return self.handler

    @classmethod
    def close_connections(cls):
        """Disconnect from all connections.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                Netmiko Close Connections

        """
        if hasattr(cls, "_CONNECTIONS"):
            cls._CONNECTIONS.close_all()

    def disconnect(self):
        """Disconnect from the current Netmiko connection.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                Disconnect

        """
        if hasattr(self, "handler"):
            self.handler.disconnect()
            delattr(self, "handler")

    def change_connection(self, alias_or_index):
        """Switch to a different connection using the index or alias.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Keywords ***
                Do Something
                    Change Connection      alias_or_index
                    ...
        Sets:
            self.c (NetmikoConnectionHandler):
                Sets the self.c object to the netmiko connection identified
                by the alias or index.
        """
        logger.info(f"Switching connection to alias {alias_or_index}")
        self.handler = self.__class__._CONNECTIONS.switch(alias_or_index)
        return self.handler

    def cli(self, command: str, timing=False) -> str:
        """Run a cli command against a current netmiko connection.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                Show Version Brief
                    ${result}=      Cli     show version brief

        Args:
            command (str):
                Cli command string to run on connected device

        Returns:
            output (str):
                Output from the Netmiko execution.
        """
        logger.info(command)
        try:
            # Use send_command_timing instead of send_command
            if timing:
                output = self.handler.send_command_timing(command, delay_factor=2)
            else:
                output = self.handler.send_command(command)
        except Exception as e:
            raise NetmikoError(str(e)) from e
        self.loghtml.cli(self.handler.initial_prompt, command, output)
        return output

    def cli_expect(self, command: str, expect: str) -> str:
        """Run a cli command against a current netmiko connection
        and expect a string in the result.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                Show Version Brief
                    ${result}=      Cli expect     load config merge    <expect_string>

        Args:
            command (str):
                Cli command string to run on connected device
            expect (str):
                String expected to be returned from the command.

        Returns:
            output (str):
                Output from the Netmiko execution.
        """
        logger.info(command)
        try:
            output = self.handler.send_command(command, expect=expect)
        except Exception as e:
            raise NetmikoError(str(e)) from e
        self.loghtml.cli(self.handler.initial_prompt, command, output)
        return output

    def cli_ttp(self, command: str, template: str, timing: bool = False):
        """Parse output from the CLI using TTP and return a python object.

        https://ttp.readthedocs.io/en/latest/

        This command expects the TTP template to be stored in a robot variable.

        It is often useful to use a seperate file to import the variable.
        I prefer using .py files and setting the string:

        template_cisco.py
            show_interface = '''interface {{interface}}'''

        Then in *** Settings *** you can declare:
            Variables  template_cisco.py


        RobotFramework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                ${result}=        Cli ttp       show interface     ${show_interface}

        Args:
            command (str):
                Command that will be converted to json output.
            template (str):
                Command that will be converted to json output.

        Returns:
            output (dict|list):
                Converted variables from the CLI output.
        """
        output = self.cli(command, timing=timing)
        _vars = self.parse_ttp_text(output, template)
        self.loghtml.cli_parse(self.ip, command, output, template, _vars)
        # TTP returns results in a list(list()) format by default - which can be annoying.
        # Here, we just return the first list if there are no advanced TTP groupings, etc.
        if len(_vars) == 1:
            return _vars[0]
        return _vars

    def cli_json(self, command: str, timing: bool = False):
        """Parse JSON output from the CLI and return a python object.

        This will append '| json' to your CLI command
        and return the results as a python object.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                ${json_result}=   Cli Json      show feature

        Args:
            command (str):
                Command that will be converted to json output.

        Returns:
            output (dict|list):
                Converted json text from the CLI output.
        """
        self.cli(command, timing=timing)
        json_result = self.cli(command + " | json")
        return json.loads(json_result)

    def send_file(self, filename: str, path: str, dest: str) -> dict:
        """Send a file using SCP to the connected netmiko session.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                ${result}=      Send File       filename       path     dest

        Args:
            filename (str):
                The source file (including path) to transfer.
            dest (str):
                The full destination path and filename.

        Returns:
            transfer (dict):
                The result of the file transfer.
        """
        transfer = netmiko.file_transfer(
            self.handler,
            filename,
            dest,
            file_system=path,
            direction="put",
            overwrite_file=True,
        )
        return transfer

    def parse_ttp_text(self, text: str, template: str, force_list=False):
        """Parse a text block (often from a switch or router CLI output) using
        the Python TTP Library. This will convert the text block into python
        native lists/dictionaries for easier use with validations and other
        functions.

        Examples:
            Robot Framework

            .. code-block:: robotframework

                *** Test Case ***
                Parse CLI Output with TTP
                    ${result}=          Parse TTP Text  ${cli}  ${template}
                    Should be equal     ${result['some_ttp_var']}   my_value

        Args:
            text (str):
                Text block to parse
            template (str):
                The string-based TTP template used to match variables in
                the text

        Returns:
            ttp.result (list):
                A list of variables that were parsed from the text
        """
        # Fix newline formating as ttp does not like \r\n on windows
        # text = text.replace("\r\n", "\n")
        # Create a new ttp parser with the text and template
        parser = ttp(data=text, template=template)
        parser.parse()
        # Raise an error if no variables were found in the text block
        if not parser.result()[0]:
            raise ParserException(text, template)
        # Return the list of variables removing the padding lists ttp creates
        result = parser.result()[0]
        if isinstance(result, dict) and force_list:
            return [result]
        return result

    def push_config(self, config: list, cmd_verify: bool = False) -> str:
        """Push a list of configuration items to the device.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                Push Config  ${list_of_config_commands}

        Args:
            config (list):
                List of configuration commands to send to the device.

        Returns:
            output (str):
                Output from the netmiko session.
        """
        try:
            logger.info(config)
            output = self.handler.send_config_set(
                config, delay_factor=1, cmd_verify=cmd_verify
            )
            logger.info(output)
            if self.handler.device_type in self.commit_os:
                try:
                    self.handler.commit()
                    self.handler.exit_config_mode()
                except ValueError as e:
                    if self.handler.device_type == "cisco_xr":
                        # Do a show configuration failed (nxos devices)
                        output = self.handler.send_command("show configuration failed")
                        logger.error(output)
                        # Abort the configuration
                        self.handler.send_command("abort", auto_find_prompt=False)
                    else:
                        raise ValueError(e)
            return output
        except Exception as e:
            raise NetmikoError(str(e)) from e

    def generate_config(self, jinja_file: str, yaml_file: str) -> str:
        """Generate configuration lines from a Jinja and Yaml file.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                ${list_of_config_commands}=   Generate Config  ${jinja_file}    ${yaml_file}

        Args:
            jinja_file (str):
                The path to the jinja template

            yaml_file (str):
                The path to the yaml file

        Returns:
            config (list):
                Rendered jinja/yaml file converted to a list.
        """
        config_vars = yaml.load(open(yaml_file, "r"), Loader=yaml.Loader)

        # Configure Jinja to look in the same folder as the yaml file
        env = Environment(
            loader=FileSystemLoader(searchpath=path.dirname(jinja_file)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template(path.basename(jinja_file))
        config = template.render(config=config_vars)

        logger.info(config)
        return config.split("\n")

    def clear_counters(self):
        """Run clear counters command on the current device.

        Robot framework Examples:

            .. code-block:: robotframework

                *** Test Cases ***
                Clear Counters

        """
        self.handler.send_command("clear counters", expect_string=r"confirm")
        self.handler.send_command("\n", expect_string=r"#")

    def f5_merge_config(self, _file):
        """Merge an F5 configuration file to the device.

        Args:
            device (NetmikoSession):
                A netmiko session (provided by Netmiko Switch)

            _str (str): An irule text definition.

        """
        if "f5" not in self.device_type:
            raise Exception("Device must be an F5 device.")
        self.handler.send_command_timing("load sys config merge from-terminal")
        with open(_file, "r") as f:
            config = f.read()
            self.handler.send_command_timing(config)
        # Send CTRL + D
        self.handler.send_command_timing("\x04")
        self.handler.send_command("\r")
