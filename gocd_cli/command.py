from collections import defaultdict
import inspect

from gocd_cli.utils import dasherize_name
from gocd_cli.exceptions import MissingDocumentationError


class BaseCommand(object):
    @classmethod
    def _get_or_raise(cls, attr, exception, message=None):
        value = getattr(cls, attr, None)
        if not value:
            if not message:
                message = 'Command "{0}" has no "{1}" string set.'.format(cls.__name__, attr)

            raise exception(message)

        return value

    @classmethod
    def get_usage(cls):
        format_args = defaultdict(str)
        format_args.update(
            usage_summary=cls.get_usage_summary(),
        )

        return cls._get_or_raise('usage', MissingDocumentationError).format(**format_args)

    @classmethod
    def get_usage_summary(cls):
        return cls._get_or_raise('usage_summary', MissingDocumentationError)

    @classmethod
    def get_call_documentation(cls):
        pass
