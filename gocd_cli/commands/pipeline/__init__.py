from gocd_cli.command import BaseCommand

from .retrigger_failed import RetriggerFailed

__all__ = ['Pause', 'RetriggerFailed', 'Trigger', 'Unlock']


def unlock_pipeline(pipeline):
    response = pipeline.status()

    if response and response['locked']:
        return pipeline.unlock()
    else:
        return False


class Trigger(BaseCommand):
    usage = """
    Flags:
        unlock: Whether the pipeline should be unlocked if it's locked.
                Default: false
    """
    usage_summary = 'Triggers the named pipeline'

    def __init__(self, server, name, unlock=False):
        self.pipeline = server.pipeline(name)
        self.unlock = unlock

    def run(self):
        if self.unlock:
            unlock_pipeline(self.pipeline)

        return self.pipeline.schedule()


class Unlock(BaseCommand):
    usage = ' '
    usage_summary = 'Unlocks the named pipeline if it\'s currently locked'

    def __init__(self, server, name):
        self.pipeline = server.pipeline(name)

    def run(self):
        return unlock_pipeline(self.pipeline)


class Pause(BaseCommand):
    usage = ' '
    usage_summary = 'Pauses the named pipeline'

    def __init__(self, server, name):
        self.pipeline = server.pipeline(name)

    def run(self):
        response = self.pipeline.status()

        if response and not response['paused']:
            return self.pipeline.pause()
        else:
            return False
