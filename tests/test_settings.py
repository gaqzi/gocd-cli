from os import path

import pytest

from gocd_cli.settings import (
    EnvironmentSettings,
    IniSettings,
    Settings,
)


@pytest.fixture
def settings():
    return Settings(
        prefix='GOCD',
        section='gocd',
        filename=path.join(path.dirname(__file__), 'support/gocd-cli.cfg')
    )


@pytest.fixture
def ini_settings():
    return IniSettings(
        section='gocd',
        filename=path.join(path.dirname(__file__), 'support/gocd-cli.cfg')
    )


@pytest.fixture
def ini_settings_no_section():
    return IniSettings(
        section='nonexistent',
        filename=path.join(path.dirname(__file__), 'support/gocd-cli.cfg')
    )


@pytest.fixture
def settings_encrypted():
    return Settings(
        prefix='GOCD',
        section='gocd',
        filename=path.join(path.dirname(__file__), 'support/gocd-cli-encrypted-password.cfg')
    )


@pytest.fixture
def env_settings():
    return EnvironmentSettings(prefix='GOCD')


def test_reads_configuration_key_from_ini(ini_settings):
    assert ini_settings.get('server') == 'http://localhost:8153'


def test_reads_non_existant_key_from_ini_returns_none(ini_settings):
    assert ini_settings.get('nonexistent') is None


def test_reads_from_nonexistent_ini_section_returns_none(ini_settings_no_section):
    assert ini_settings_no_section.get('nonexistent') is None


def test_ini_section_is_made_lowercase():
    settings = IniSettings(
        section='GOCD',
        filename=path.join(path.dirname(__file__), 'support/gocd-cli.cfg')
    )

    assert settings.get('server') == 'http://localhost:8153'


def test_reads_configuration_key_from_env(env_settings, monkeypatch):
    val = 'http://localhost:8153'
    monkeypatch.setenv('GOCD_SERVER', val)

    assert env_settings.get('server') == val


def test_configuration_prefix_is_made_uppercase(monkeypatch):
    monkeypatch.setenv('GOCD_SERVER', 'hello')
    settings = EnvironmentSettings(prefix='gocd')

    assert settings.get('server') == 'hello'


def test_reads_non_existant_key_from_env_returns_none(env_settings, monkeypatch):
    monkeypatch.delenv('GOCD_NONEXISTENT', raising=False)

    assert env_settings.get('nonexistent') is None


def test_settings_should_read_env_first(settings, monkeypatch):
    monkeypatch.setenv('GOCD_SERVER', 'hello')

    assert settings.get('server') == 'hello'


def test_settings_should_fallback_to_ini_when_nothing_in_env(settings, monkeypatch):
    monkeypatch.delenv('GOCD_USER', raising=False)

    assert settings.get('user') == 'ba'


def test_settings_should_return_none_when_nothing_anywhere(settings, monkeypatch):
    monkeypatch.delenv('GOCD_NONEXISTENT', raising=False)

    assert settings.get('nonexistent') is None


def test_settings_looks_for_encrypted_version_when_encryption_module_set(settings_encrypted):
    assert settings_encrypted.get('password') == 'super secret'
    assert settings_encrypted.get('user') == 'ba'
