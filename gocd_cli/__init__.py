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


def get_command_module(command):  # TODO: rename this function, I just don't know to what
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
            arg = arg[2:]

            if '=' in arg:
                key, value = arg.split('=')
                kwargs[key.replace('-', '_')] = value
            else:
                split_key = arg.replace('-', '_')
        elif split_key:
            kwargs[split_key] = arg
            split_key = None
        else:
            positional_args.append(arg)

    return positional_args, kwargs


def get_command(go_server, command, subcommand, *args):  # TODO: Think about this, it feels ugly
    """

    Raises:
        AttributeError: when the `subcommand` doesn't exist in the
            `command` package
        ImportError: when the package `command` doesn't exist.
        TypeError: when failing to initialize the `subcommand`
    """
    try:
        command_package = get_command_module(command)
    except ImportError as exc:
        raise ImportError('gocd_cli.commands: {0}'.format(exc))

    class_name = classify_name(subcommand)
    try:
        Klass = getattr(command_package, class_name)
    except AttributeError as exc:
        raise AttributeError('{0}: {1}'.format(command_package.__name__, exc))
    args, kwargs = format_arguments(*args)

    try:
        return Klass(go_server, *args, **kwargs)
    except TypeError as exc:
        raise TypeError('{0}: {1}'.format(class_name, exc))
