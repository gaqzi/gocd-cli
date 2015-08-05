from gocd_cli.command import BaseCommand

from .retrigger_failed import RetriggerFailed

__all__ = ['RetriggerFailed', 'Trigger', 'Unlock']


class Trigger(BaseCommand):
    usage_summary = 'Triggers the named pipeline'

    def __init__(self, server, name):
        self.pipeline = server.pipeline(name)

    def run(self):
        return self.pipeline.schedule()


class Unlock(BaseCommand):
    usage = ' '
    usage_summary = 'Unlocks the named pipeline if it\'s currently locked'

    def __init__(self, server, name):
        self.pipeline = server.pipeline(name)

    def run(self):
        response = self.pipeline.status()

        if response and response['locked']:
            return self.pipeline.unlock()
        else:
            return False
