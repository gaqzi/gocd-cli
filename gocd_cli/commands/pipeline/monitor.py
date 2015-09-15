import datetime as dt
import time
from gocd_cli.command import BaseCommand

__all__ = ['Monitor']


class Monitor(BaseCommand):
    usage = """
    Checks whether a pipeline has run after a given time, finished successfully,
    and warns if it has been running for a long time.

    The alerting codes corresponds to the same in Nagios.

    Flags:
        ran_after: A time today for which the script should've run
            after. If the time is before now assume the previous day
        warn_run_time: If the current stage in the pipeline has been
            running for longer than this warn
        crit_run_time: If it has been for running longer than this many
            minutes raise a critical warning

    Exits:
        0: Everything is green
        1: When there's a warning
        2: When there's a critical warning
    """
    usage_summary = 'Check whether a pipeline has run successfully'
    __now = None
    _ran_after = None

    final_job_states = ['Passed', 'Failed']  # States when a job/stage isn't doing anything more

    def __init__(self, server, name, ran_after=None, warn_run_time=30, crit_run_time=60):
        self.name = name
        self.pipeline = server.pipeline(name)
        self.ran_after = ran_after
        self.warn_run_time = warn_run_time
        self.crit_run_time = crit_run_time

        self.currently_running = False
        self.running_since = []
        self._started_at = None

    def run(self):
        response = self.pipeline.history()
        if not response:
            raise Exception('Cannot continue like this. Response was invalid!')

        for stage in response['pipelines'][0]['stages']:
            stage_result = stage.get('result', None)

            if stage_result == 'Failed':
                return self._return_value('Pipeline "{0}" failed'.format(self.name), 'critical')
            elif stage_result == 'Unknown' and stage['scheduled'] and stage['jobs']:
                self._process_currently_running_stage(stage)
            elif stage['jobs']:  # Has jobs but isn't scheduled, means it has finished running
                scheduled_at = self._get_earliest('scheduled_date', stage)
                self._update_started_at(scheduled_at)

        return self._current_pipeline_state()

    def _process_currently_running_stage(self, stage):
        if not self.currently_running:
            self.currently_running = next(
                (True for job in stage['jobs'] if job['state'] not in self.final_job_states),
                False
            )

        scheduled_at = self._get_earliest('scheduled_date', stage)
        self.running_since.append(scheduled_at)
        self._update_started_at(scheduled_at)

    def _current_pipeline_state(self):
        if self.currently_running:
            longest_running = min(self.running_since)
            current_run_time = (self._now - longest_running)

            if current_run_time >= self._warn_time:
                return self._return_value(
                    'Pipeline "{0}" stalled at "{1}", running for {2} seconds'.format(
                        self.name,
                        self._current_timestamp(),
                        current_run_time / 1000
                    ),
                    'critical' if current_run_time >= self._crit_time else 'warning'
                )
            else:
                return self._return_value('Successful')
        elif self.ran_after >= self.started_at:
            return self._return_value('Pipeline "{0}" has not run after "{1}".'.format(
                self.name,
                self._format_timestamp(self.ran_after)
            ), 'critical')
        else:
            return self._return_value('Successful')

    @property
    def _now(self):
        if not self.__now:
            self.__now = time.time() * 1000

        return self.__now

    @property
    def _warn_time(self):
        return self.warn_run_time * 60 * 1000

    @property
    def _crit_time(self):
        return self.crit_run_time * 60 * 1000

    @property
    def ran_after(self):
        return self._ran_after

    @ran_after.setter
    def ran_after(self, value):
        if not value:
            return

        now = dt.datetime.fromtimestamp(self._now / 1000)
        val = dt.time(*map(lambda x: int(x), value.split(':')))
        val = dt.datetime.now().replace(
            hour=val.hour,
            minute=val.minute,
            second=val.second,
            microsecond=val.microsecond
        )

        if now >= val:
            self._ran_after = time.mktime(val.timetuple()) * 1000
        else:
            self._ran_after = time.mktime((val - dt.timedelta(days=1)).timetuple()) * 1000

    @property
    def started_at(self):
        return self._started_at

    def _return_value(self, message, exit_status='ok'):
        exit_code = 0
        if exit_status == 'warning':
            exit_code = 1
        elif exit_status == 'critical':
            exit_code = 2

        return dict(
            output='{status}: {message}'.format(status=exit_status.upper(), message=message),
            exit_code=exit_code,
        )

    def _current_timestamp(self):
        return self._format_timestamp(self._now)

    def _format_timestamp(self, unix_timestamp):
        return dt.datetime.fromtimestamp(unix_timestamp / 1000).strftime('%Y-%m-%dT%H:%M:%S')

    def _get_earliest(self, time_key, stage):
        return min(map(lambda job: job[time_key], stage['jobs']))

    def _update_started_at(self, scheduled_at):
        if not self._started_at or self._started_at > scheduled_at:
            self._started_at = scheduled_at

        return self.started_at