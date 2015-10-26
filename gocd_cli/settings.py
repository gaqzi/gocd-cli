import ConfigParser
from os import getenv


class BaseSettings(object):
    def __init__(self, **kwargs):
        pass

    def get(self, option):
        """Tries to find a configuration variable in the current store.
        Returns:
          string, number, boolean or other representation of what was found or
          None when nothing found.
        """
        return None


class IniSettings(BaseSettings):
    """Reads configuration from ini files scoped to a specific section.
    Args:
      section: The ini file section this configuration is scoped to
      filename: The path to the ini file to use
    Example:
      settings = IniSettings(section='main',
                             filename='gocd-cli.cfg')
      settings.get('api_key')
    """
    def __init__(self, **kwargs):
        self.section = kwargs.get('section', '').lower()
        self.config = ConfigParser.SafeConfigParser()

        filename = kwargs.get('filename', None)
        if filename:
            self.config.read(filename)

        super(IniSettings, self).__init__(**kwargs)

    def get(self, option):
        try:
            return self.config.get(self.section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return super(IniSettings, self).get(option)


class EnvironmentSettings(BaseSettings):
    """Reads configuration variables from the system environment.
    Args:
      prefix: converted to uppercase and used with the option name
          to find an environment variable to read.
    Example:
      settings = EnvironmentSettings(prefix='GOCD')
      settings.get('user')  # reads: GOCD_USER
    """
    def __init__(self, **kwargs):
        self.prefix = kwargs.get('prefix', '').upper()

        super(EnvironmentSettings, self).__init__(**kwargs)

    def get(self, option):
        val = getenv(
            '{0}_{1}'.format(self.prefix, option.upper()),
            None
        )

        if val is None:
            return super(EnvironmentSettings, self).get(option)
        else:
            return val


class EncryptedSettings(BaseSettings):
    """Will look for, and decrypt, encrypted values for keys if
    encryption module is set. The encryption module will be dynamically
    imported and giving the password to the module has to happen out
    of band.

    This relies on being able to get the ciphertext from the other
    methods of retrieving configuration values. Therefore it has to be
    listed first in the mixed in class.
    """
    encryption_module = False

    def __init__(self, **kwargs):
        super(EncryptedSettings, self).__init__(**kwargs)

        encryption_module = self.get('encryption_module')
        if encryption_module:
            mod = __import__(encryption_module, fromlist=('',))
            if mod:
                self.encryption_module = mod

    def get(self, option):
        if self.encryption_module:
            val = super(EncryptedSettings, self).get('{0}_encrypted'.format(option))
            if val:
                return self._decrypt(val)

        return super(EncryptedSettings, self).get(option)

    def _decrypt(self, val):
        return self.encryption_module.decrypt(val)


class Settings(EncryptedSettings, EnvironmentSettings, IniSettings):
    def __init__(self, prefix, section, filename=None):
        """Will try to read configuration from environment variables and ini
        files, if no value found in either of those ``None`` is
        returned.

        Args:
            prefix: The environment variable prefix.
            section: The ini file section this configuration is scoped to
            filename: The path to the ini file to use
        """
        options = dict(prefix=prefix, section=section, filename=filename)

        super(Settings, self).__init__(**options)
