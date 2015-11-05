from os import path

import pytest

from gocd import Server
from gocd.api import Pipeline
from gocd_cli.commands.settings import (
    Decrypt,
    Encrypt
)
from gocd_cli.settings import Settings
from mock import MagicMock


@pytest.fixture
def go_server():
    server = MagicMock(spec=Server)
    server.pipeline.return_value = MagicMock(spec=Pipeline)

    return server


def settings_encrypted():
    return Settings(
        prefix='GOCD',
        section='gocd',
        filename=path.join(path.dirname(__file__), '../support/gocd-cli-encrypted-password.cfg')
    )


class EncryptionBase(object):
    @pytest.fixture(autouse=True)
    def mock_settings(self, monkeypatch):
        monkeypatch.setattr('gocd_cli.commands.settings.get_settings', settings_encrypted)


class TestEncrypt(EncryptionBase):
    def test_encrypt(self, go_server):
        cmd = Encrypt(go_server, 'hello')

        assert cmd.run()['output'].endswith('Ciphertext = uryyb')

    def test_fetch_encrypted_key(self):
        cmd = Encrypt(go_server, key='password')

        assert cmd.run()['output'].endswith('password_encrypted = fhcre frperg')


class TestDecrypt(EncryptionBase):
    def test_decrypt(self, go_server):
        cmd = Decrypt(go_server, 'uryyb')

        assert cmd.run()['output'].endswith('Plaintext = hello')

    def test_fetch_encrypted_key(self):
        cmd = Decrypt(go_server, key='password_encrypted')

        assert cmd.run()['output'].endswith('password = super secret')
