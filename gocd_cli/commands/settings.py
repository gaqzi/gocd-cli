from __future__ import print_function

from gocd_cli.command import BaseCommand
from gocd_cli.utils import get_settings

__all__ = ['Decrypt', 'Encrypt']


class BaseEncryptionCommand(object):
    _encryption_module = None
    _settings = None

    @property
    def settings(self):
        if self._settings is None:
            self._settings = get_settings()

        return self._settings

    @property
    def encryption_module(self):
        if self._encryption_module is None:
            mod = self.settings.get('encryption_module') or 'gocd_cli.encryption.caesar'
            self._encryption_module = __import__(mod, fromlist=('',))

        return self._encryption_module


class Encrypt(BaseCommand, BaseEncryptionCommand):
    usage = """One of either plaintext or key can be passed in
    Flags:
        plaintext: A string to encrypt
        key: A configuration key from the settings file
    """
    usage_summary = 'Encrypts the passed in plaintext or key to ciphertext'

    def __init__(self, server, plaintext=None, key=None):
        self.server = server
        self._plaintext = plaintext
        self._key = key

    @property
    def plaintext(self):
        if self._key:
            return self.settings.get(self._key)
        else:
            return self._plaintext

    def label(self):
        if self._key:
            return '{0}_encrypted'.format(self._key.replace('_encrypted', ''))
        else:
            return 'Ciphertext'

    def run(self):
        ciphertext = self.encryption_module.encrypt(self.plaintext)

        return self._return_value('{0}\n{1}'.format(
            'encryption_module = {0}'.format(self.encryption_module.__name__),
            '{0} = {1}'.format(self.label(), ciphertext)
        ), exit_code=0)


class Decrypt(BaseCommand, BaseEncryptionCommand):
    usage = """One of either ciphertext or key can be passed in
    Flags:
        ciphertext: A string to decrypt
        key: A configuration key from the settings file
    """
    usage_summary = 'Decrypts the passed in ciphertext or key to plaintext'

    def __init__(self, server, ciphertext=None, key=None):
        self.server = server
        self._ciphertext = ciphertext
        self._key = key

    @property
    def ciphertext(self):
        if self._key:
            return self.settings.get(self._key)
        else:
            return self._ciphertext

    def label(self):
        if self._key:
            return self._key.replace('_encrypted', '')
        else:
            return 'Plaintext'

    def run(self):
        plaintext = self.encryption_module.decrypt(self.ciphertext)

        return self._return_value('{0}\n{1}'.format(
            'encryption_module = {0}'.format(self.encryption_module.__name__),
            '{0} = {1}'.format(self.label(), plaintext),
        ), exit_code=0)
