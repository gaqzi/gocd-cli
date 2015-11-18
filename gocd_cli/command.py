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
        usage = cls._get_or_raise('usage', MissingDocumentationError)

        return '{call_documentation}\n\n{usage_summary}\n\n{usage}\n'.format(
            call_documentation=cls.get_call_documentation(),
            usage_summary=cls.get_usage_summary(),
            usage=inspect.cleandoc(usage),
        )

    @classmethod
    def get_usage_summary(cls):
        return cls._get_or_raise('usage_summary', MissingDocumentationError)

    @classmethod
    def get_call_documentation(cls):
        def get_arg_names():
            args, varargs, keywords, defaults = inspect.getargspec(cls.__init__)
            if args[0] == 'self':
                del args[0]
            if args[0] == 'server':
                del args[0]

            kwargs = args[-len(defaults):] if defaults else []
            positional = args[:-len(kwargs)] if kwargs else args

            return positional, kwargs
        args, kwargs = get_arg_names()

        return '{command} {args} {kwargs}'.format(
            command=dasherize_name(cls.__name__),
            args=' '.join('<{0}>'.format(arg) for arg in args),
            kwargs=' '.join('[--{0}]'.format(arg.replace('_', '-')) for arg in kwargs),
        ).strip()

    def _return_value(self, output, exit_code):
        if isinstance(exit_code, bool):
            exit_code = 0 if exit_code else 2

        return dict(
            exit_code=exit_code,
            output=output,
        )
