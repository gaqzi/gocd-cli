import os.path
import pkgutil
import pwd
import re
import string

from gocd_cli import commands
from gocd_cli.settings import Settings
import gocd


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
    return __import__('gocd_cli.commands.{0}'.format(command), fromlist=(str(command),))


def expand_user(path):
    """Expands ~/path to /home/<current_user>/path

    On POSIX systems does it by getting the home directory for the
    current effective user from the passwd database. On other systems
    do it by using :func:`os.path.expanduser`

    Args:
        path (str): A path to expand to a user's home folder

    Returns:
        str: expanded path
    """
    if not path.startswith('~'):
        return path

    if os.name == 'posix':
        user = pwd.getpwuid(os.geteuid())
        return path.replace('~', user.pw_dir, 1)
    else:
        return os.path.expanduser(path)


def is_file_readable(path):
    path = expand_user(path)
    return os.path.isfile(path) and os.access(path, os.R_OK)


def format_arguments(*args):
    """
    Converts a list of arguments from the command line into a list of
    positional arguments and a dictionary of keyword arguments.

    Handled formats for keyword arguments are:
    * --argument=value
    * --argument value

    Args:
      *args (list): a list of arguments

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
                key, value = arg.split('=', 1)
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


def get_settings(section='gocd', settings_paths=('~/.gocd/gocd-cli.cfg', '/etc/go/gocd-cli.cfg')):
    """Returns a `gocd_cli.settings.Settings` configured for settings file

    The settings will be read from environment variables first, then
    it'll be read from the first config file found (if any).

    Environment variables are expected to be in UPPERCASE and to be prefixed
    with `GOCD_`.

    Args:
      section: The prefix to use for reading environment variables and the
        name of the section in the config file. Default: gocd
      settings_path: Possible paths for the configuration file.
        Default: `('~/.gocd/gocd-cli.cfg', '/etc/go/gocd-cli.cfg')`

    Returns:
        `gocd_cli.settings.Settings` instance
    """
    if isinstance(settings_paths, basestring):
        settings_paths = (settings_paths,)

    config_file = next((path for path in settings_paths if is_file_readable(path)), None)
    if config_file:
        config_file = expand_user(config_file)

    return Settings(prefix=section, section=section, filename=config_file)


def get_go_server(settings=None):
    """Returns a `gocd.Server` configured by the `settings`
    object.

    Args:
      settings: a `gocd_cli.settings.Settings` object.
        Default: if falsey calls `get_settings`.

    Returns:
      gocd.Server: a configured gocd.Server instance
    """
    if not settings:
        settings = get_settings()

    return gocd.Server(
        settings.get('server'),
        user=settings.get('user'),
        password=settings.get('password'),
    )
