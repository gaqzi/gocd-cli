from gocd_cli.command import BaseCommand

from .retrigger_failed import RetriggerFailed

__all__ = ['RetriggerFailed', 'Trigger']


class Trigger(BaseCommand):
    usage_summary = 'Triggers the named pipeline'

    def __init__(self, server, name):
        self.pipeline = server.pipeline(name)

    def run(self):
        return self.pipeline.schedule()
