from gocd_cli.command import BaseCommand
from gocd_cli.utils import get_settings

from .check import Check
from .retrigger_failed import RetriggerFailed

__all__ = [
    'Check',
    'CheckAll',
    'List',
    'Pause',
    'RetriggerFailed',
    'Trigger',
    'Unlock',
    'Unpause',
]


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


class CheckAll(BaseCommand):
    usage = """
    Checks that all pipelines except those explicitly ignored are green
    and not stalled.

    Configuration is done in by the check_all section of the
    gocd-cli.cfg.

    For usage of the flags and return statuses see the check command.
    """
    usage_summary = 'Checks all pipelines to be green/non-stalled'

    exit_code = 0
    error_messages = []

    OK_STATUS = 0
    PAUSED_STATUS = 3

    def __init__(self, server, warn_run_time=30, crit_run_time=60, skip_paused=True):
        self.config = get_settings('check_all')
        self.server = server
        self.crit_run_time = crit_run_time
        self.warn_run_time = warn_run_time
        self.skip_paused = skip_paused

    def run(self):
        ignored_pipelines = (self.config.get('ignored_pipelines') or '').split(',')
        for pipeline in self.server.pipeline_groups().pipelines:
            if pipeline in ignored_pipelines:
                continue

            response = Check(
                self.server,
                pipeline,
                warn_run_time=self.warn_run_time,
                crit_run_time=self.crit_run_time,
            ).run()
            if response['exit_code'] != self.OK_STATUS:
                if self.skip_paused and response['exit_code'] == self.PAUSED_STATUS:
                    continue

                if(response['exit_code'] != self.PAUSED_STATUS
                   and response['exit_code'] > self.exit_code):
                    self.exit_code = response['exit_code']

                self.error_messages.append(response['output'])

        if self.exit_code != self.OK_STATUS:
            return self._return_value('\n'.join(self.error_messages), self.exit_code)
        else:
            return self._return_value('OK: All green', self.OK_STATUS)


class List(BaseCommand):
    usage = ' '
    usage_summary = 'Lists all pipelines with their current status'

    def __init__(self, server):
        self.server = server

    def run(self):
        for pipeline in self.server.pipeline_groups().pipelines:
            status = self.server.pipeline(pipeline).status()
            if not status:
                print 'Error getting status for "{0}"'.format(pipeline)
                exit(3)

            print '{0}: {1}'.format(pipeline, self._format_status(status.payload))

    def _format_status(self, status):
        return ', '.join(('{0}={1}'.format(k, v) for k, v in status.items()))


class GetArtifact(BaseCommand):
    usage = ' '
    usage_summary = 'Gets a named artifact from a stage/job'

    final_job_states = ['Passed', 'Failed']  # States when a job/stage isn't doing anything more

    def __init__(self, server, name, stage, filename, save_to='.', job=None, counter=None):
        self.server = server
        self.name = name
        self.stage = stage
        self.filename = filename
        self.save_to = save_to
        self.job = job
        self.counter = counter

        self.pipeline = self.server.pipeline(name)

    def run(self):
        pipeline_run = self._get_run()
        stage = next(
            (stage for stage in pipeline_run['stages'] if stage['name'] == self.stage),
            None
        )
        if not stage['result'] in self.final_job_states:
            return self._return_value(
                'Stage {0} is "{1}", it needs to be in a final state to download a file'.format(
                    self.name,
                    self.stage
                ),
                1
            )


        #
        # if pipeline_run['result'] not in self.final_job_states:
        #

        # pipeline_run['status']


    def _get_run(self):
        if self.counter is None:
            response = self.pipeline.history()
            if not response:
                raise Exception('Cannot continue like this. Response was invalid!')

            last_run = response['pipelines'][0]
            self.counter = last_run['counter']

            return last_run
        else:
            return self.pipeline.instance(self.counter)
