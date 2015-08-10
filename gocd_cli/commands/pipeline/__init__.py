from gocd_cli.command import BaseCommand

from .retrigger_failed import RetriggerFailed

__all__ = ['Pause', 'RetriggerFailed', 'Trigger', 'Unlock', 'Unpause']


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
        variables: A comma separated list of key=value pairs that will
          be passed to the pipeline.
          Example: SHARED_SECRET=Mellon,SECOND=Really Im first
        secure_variables: A comma separated list of key=value pairs.
    """
    usage_summary = 'Triggers the named pipeline'

    def __init__(self, server, name, unlock=False, variables=None, secure_variables=None):
        self.pipeline = server.pipeline(name)
        self.unlock = str(unlock).lower().strip() == 'true'
        self.variables = self._convert_to_dict(variables)
        self.secure_variables = self._convert_to_dict(secure_variables)

    def run(self):
        if self.unlock:
            unlock_pipeline(self.pipeline)

        return self.pipeline.schedule(
            variables=self.variables,
            secure_variables=self.secure_variables
        )

    def _convert_to_dict(self, args):
        # XXX: I would like to find a better way of dealing with this,
        # but I think I should instead focus on getting a better way of
        # parsing arguments altogether. And allow for it to be passed
        # multiple times there instead.
        if not args:
            return None

        variables = {}
        for arg in args.split(','):
            k, v = arg.split('=')
            variables[k] = v

        return variables


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


class Unpause(BaseCommand):
    usage = ' '
    usage_summary = 'Unpauses the named pipeline'

    def __init__(self, server, name):
        self.pipeline = server.pipeline(name)

    def run(self):
        response = self.pipeline.status()

        if response and response['paused']:
            return self.pipeline.unpause()
        else:
            return False
