from gocd.api.response import Response
from gocd_cli.command import BaseCommand

__all__ = ['RetriggerFailed']


class RetriggerFailed(BaseCommand):
    usage = """
    Flags:
        counter: the pipeline counter to check. Default: latest
        stage: if given the pipeline will only be retriggered if
               this stage failed
        retrigger: possible values (pipeline, stage) default pipeline.
                   When pipeline and there's a failed stage retriggers the pipeline.
                   When stage and there's a failure retriggers only that stage.
    """
    usage_summary = 'Retrigger a pipeline/stage that has failed'

    def __init__(self, server, name, counter=None, stage=None, retrigger=None):
        assert counter is None or int(counter), '"counter" needs to be an integer'
        assert retrigger in ('pipeline', 'stage', None), (
            '"retrigger" needs to be one of "pipeline" or "stage"'
        )

        self.counter = counter
        self.stage = stage
        self.server = server
        self.pipeline = server.pipeline(name)

        self.retrigger_type = retrigger or 'pipeline'

    def run(self):
        response = self.pipeline.history()
        if not response:
            raise Exception('Cannot continue like this. Response was invalid!')

        pipeline_run = self._get_run(response)

        if self._did_the_run_fail(pipeline_run):
            return self._retrigger(response)

        return None

    def _get_run(self, response):
        if self.counter is None:
            last_run = response['pipelines'][0]
            self.counter = last_run['counter']

            return last_run
        else:
            return self.pipeline.instance(self.counter)

    def _did_the_run_fail(self, last_run):
        for stage in last_run['stages']:
            failed = stage['result'] == 'Failed'

            if(self.stage is None or self.stage == stage['name']) and failed:
                return stage

        return False

    def _retrigger(self, response):
        self._unlock()

        if self.retrigger_type == 'pipeline':
            return self.pipeline.trigger()
        else:
            self.pipeline.server.add_logged_in_session(response)
            return Response._from_request(self.pipeline.server.post(
                'go/run/{pipeline}/{counter}/{stage}'.format(
                    pipeline=self.pipeline.name,
                    counter=self.counter,
                    stage=self.stage,
                ),
            ))

    def _unlock(self):
        response = self.pipeline.unlock()
        if response or response.status_code == 406:
            return True
        else:
            raise Exception('Failed to unlock the pipeline')
