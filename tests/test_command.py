import pytest

from gocd_cli.command import BaseCommand
from gocd_cli.exceptions import MissingDocumentationError


class FakeCommand(BaseCommand):
    usage_summary = "I'm merely an example of things to come"
    usage = """
    {usage_summary}

    Args:
        something: something else
        some-more: the other thing
    """

    def __init__(self, server, name, limit=10, failure_mode=False):
        pass


class TestBaseCommandDocumentation(object):
    def test_missing_usage_summary_raises_document_missing_error(self):
        with pytest.raises(MissingDocumentationError) as exc:
            BaseCommand.get_usage_summary()

        assert 'Command "BaseCommand" has no "usage_summary" string set.' in str(exc)

    def test_missing_usage_raises_document_missing_error(self):
        with pytest.raises(MissingDocumentationError) as exc:
            BaseCommand.usage_summary = 'something'
            BaseCommand.get_usage()

        assert 'Command "BaseCommand" has no "usage" string set.' in str(exc)

    def test_usage_uses_usage_summary(self):
        assert FakeCommand.get_usage_summary()
        assert FakeCommand.get_usage_summary() in FakeCommand.get_usage()

    def test_get_call_documentation(self):
        documentation = FakeCommand.get_call_documentation()

        assert 'fake-command' in documentation
        assert 'fake-command <name>' in documentation
        assert 'fake-command <name> [--limit] [--failure-mode]' in documentation
