__import__('pkg_resources').declare_namespace(__name__)

import re
import string
import pkgutil

from gocd_cli import commands

__version__ = '0.1.0'


def dasherize_name(name):
    def replace(match):
        return '{0}{1}'.format(
            '-' if match.start() > 0 else '',
            match.group(1).lower()
        )

    return re.sub(r'([A-Z])', replace, name)


def classify_name(name):
    return string.capwords(name, '-').replace('-', '')


def list_commands():
    return [module[1] for module in pkgutil.walk_packages(commands.__path__)]


def get_command_module(command):
    return __import__('gocd_cli.commands.{0}'.format(command), fromlist=(command,))


def format_arguments(*args):
    """
    Converts a list of arguments from the command line into a list of
    positional arguments and a dictionary of keyword arguments.

    Handled formats for keyword arguments are:
    * --argument=value
    * --argument value

    Args:
        *args: a list of arguments

    Returns:
        ([positional_args], {kwargs})
    """
    positional_args = []
    kwargs = {}
    split_key = None

    for arg in args:
        if arg.startswith('--'):
            if '=' in arg:
                key, value = arg[2:].split('=')
                kwargs[key] = value
            else:
                split_key = arg[2:]
        elif split_key:
            kwargs[split_key] = arg
            split_key = None
        else:
            positional_args.append(arg)

    return positional_args, kwargs


def run_command(go_server, command, subcommand, *args):
    command_package = get_command_module(command)
    class_name = classify_name(subcommand)

    Klass = getattr(command_package, class_name)
    args, kwargs = format_arguments(*args)

    return Klass(go_server, *args)
