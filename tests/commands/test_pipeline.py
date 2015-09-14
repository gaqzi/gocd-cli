import pytest
import time

from datetime import datetime, timedelta
from gocd import Server
from gocd.api import Pipeline
from mock import MagicMock

from gocd_cli.commands.pipeline import Monitor, Pause, Trigger, Unlock, Unpause


@pytest.fixture
def go_server():
    server = MagicMock(spec=Server)
    server.pipeline.return_value = MagicMock(spec=Pipeline)

    return server


class TestTrigger(object):
    def test_triggers_the_named_pipeline(self, go_server):
        cmd = Trigger(go_server, 'Simple-Pipeline')
        cmd.run()

        go_server.pipeline.assert_called_once_with('Simple-Pipeline')
        cmd.pipeline.schedule.assert_called_once_with(variables=None, secure_variables=None)

    def test_tries_to_unlock_the_pipeline_if_asked(self, go_server):
        cmd = Trigger(go_server, 'Simple-Pipeline', unlock=True)
        cmd.pipeline.status.return_value = dict(locked=True)
        cmd.run()

        cmd.pipeline.unlock.assert_called_with()

    def test_doesnt_try_to_unlock_if_unlock_is_not_true(self, go_server):
        cmd = Trigger(go_server, 'Simple-Pipeline', unlock='false')
        cmd.pipeline.status.return_value = dict(locked=True)
        cmd.run()

        assert not cmd.pipeline.unlock.called

    def test_trigger_with_variables(self, go_server):
        cmd = Trigger(go_server, 'Keymaker', variables='PIPELINE=The-Matrix')
        cmd.run()

        cmd.pipeline.schedule.assert_called_once_with(
            variables=dict(PIPELINE='The-Matrix'),
            secure_variables=None
        )

    def test_trigger_with_secure_variables(self, go_server):
        cmd = Trigger(go_server, 'Moria', secure_variables='PASSCODE=Mellon')
        cmd.run()

        cmd.pipeline.schedule.assert_called_once_with(
            variables=None,
            secure_variables=dict(PASSCODE='Mellon')
        )


class TestUnlock(object):
    @pytest.fixture(autouse=True)
    def setup(self, go_server):
        self.cmd = Unlock(go_server, 'Simple-Pipeline')

    def test_checks_if_pipeline_is_unlocked(self):
        self.cmd.run()

        self.cmd.pipeline.status.assert_called_once_with()

    def test_doesnt_unlock_if_pipeline_is_already_unlocked(self):
        self.cmd.pipeline.status.return_value = dict(locked=False)
        self.cmd.run()

        assert not self.cmd.pipeline.unlock.called

    def test_unlocks_if_pipeline_is_locked(self):
        self.cmd.pipeline.status.return_value = dict(locked=True)
        self.cmd.run()

        self.cmd.pipeline.unlock.assert_called_with()


class BasePause(object):
    def _command(self, go_server, paused):
        cmd = self.Command(go_server, 'Simple-Pipeline')
        cmd.pipeline.status.return_value = dict(paused=paused)
        cmd.run()

        return cmd


class TestPause(BasePause):
    Command = Pause

    def test_pauses_when_unpaused(self, go_server):
        self._command(go_server, paused=False).pipeline.pause.assert_called_with()

    def test_doesnt_run_if_already_paused(self, go_server):
        assert not self._command(go_server, True).pipeline.pause.called


class TestUnpause(BasePause):
    Command = Unpause

    def test_unpauses_when_paused(self, go_server):
        self._command(go_server, paused=True).pipeline.unpause.assert_called_with()

    def test_doesnt_run_if_already_unpaused(self, go_server):
        assert not self._command(go_server, paused=False).pipeline.unpause.called


class TestMonitor(object):
    def _pipeline(self, result='Unknown', job_state='Scheduled', scheduled_minutes_back=20):
        scheduled_date = time.time() - (60 * (scheduled_minutes_back or 20))

        return {
            'stages': [
                {
                    'scheduled': True,
                    'jobs': [
                        {
                            'id': 1,
                            'state': job_state,
                            'result': result,
                            'scheduled_date': scheduled_date * 1000,
                            'name': 'defaultJob'
                        }
                    ],
                    'name': 'defaultStage',
                    'can_run': False,
                    'operate_permission': True,
                    'approval_type': 'success',
                    'counter': '1',
                    'approved_by': 'changes',
                    'result': result,
                    'rerun_of_counter': None,
                    'id': 1
                }
            ],
            'result': result
        }

    def _scheduled_pipeline(self, scheduled_minutes_back=20):
        return self._pipeline(result='Unknown', scheduled_minutes_back=scheduled_minutes_back)

    def _green_pipeline(self, scheduled_at=None):
        if scheduled_at:
            scheduled_at = divmod(int(time.time() - time.mktime(scheduled_at.timetuple())), 60)[0]

        return self._pipeline(result='Passed', scheduled_minutes_back=scheduled_at)

    def _building_pipeline(self):
        return self._pipeline(result='Unknown', job_state='Building')

    def _red_pipeline(self):
        return self._pipeline(result='Failed')

    def _running_pipeline_with_unscheduled_stage(self):
        pipeline = self._pipeline(result='Unknown', job_state='Building')
        pipeline['stages'].append(dict(
            scheduled=False,
            jobs=[],
            name="drop_migrate",
            can_run=False,
            operate_permission=True,
            approval_type=None,
            counter="1",
            approved_by=None,
            rerun_of_counter=None,
            id=0,
        ))

        return pipeline

    def test_determines_pipeline_has_stalled_warning(self, go_server):
        cmd = Monitor(go_server, 'Stalled-Pipeline', warn_run_time=10)
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._scheduled_pipeline()]
        )
        result = cmd.run()

        assert result['output'].startswith('WARNING: Pipeline "Stalled-Pipeline" stalled at')
        assert result['exit_code'] == 1

    def test_determines_pipeline_has_stalled_critical(self, go_server):
        cmd = Monitor(go_server, 'Stalled-Pipeline', warn_run_time=10, crit_run_time=15)
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._scheduled_pipeline(scheduled_minutes_back=20)]
        )
        result = cmd.run()

        assert result['output'].startswith('CRITICAL: Pipeline "Stalled-Pipeline" stalled at')
        assert result['exit_code'] == 2

    def test_determines_pipeline_is_successful(self, go_server):
        cmd = Monitor(go_server, 'Green-Pipeline')
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._green_pipeline()]
        )
        result = cmd.run()

        assert result['output'] == 'OK: Successful'
        assert result['exit_code'] == 0

    def test_determine_pipeline_is_failed(self, go_server):
        cmd = Monitor(go_server, 'Red-Pipeline')
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._red_pipeline()]
        )
        result = cmd.run()

        assert result['output'].startswith('CRITICAL: Pipeline "Red-Pipeline" failed')
        assert result['exit_code'] == 2

    def test_pipeline_is_building(self, go_server):
        """
        When pipeline state isn't Passed or Failed the pipeline should
        be assumed to be in progress.
        """
        cmd = Monitor(go_server, 'Currently-Building')
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._building_pipeline()]
        )
        result = cmd.run()

        assert result['output'].startswith('OK: Successful')

    def test_pipeline_is_building_and_has_stages_that_arent_scheduled(self, go_server):
        cmd = Monitor(go_server, 'Currently-Building')
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._running_pipeline_with_unscheduled_stage()]
        )
        result = cmd.run()

        assert result['output'].startswith('OK: Successful')

    def test_now_is_in_milliseconds(self, go_server):
        cmd = Monitor(go_server, 'Currently-Building')
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._green_pipeline()]
        )

        assert (cmd._now - time.time()) >= 1000

    def test_determine_pipeline_has_run_after_given_time_in_the_past(self, go_server):
        scheduled_at = datetime.now() - timedelta(hours=1)
        scheduled_at = scheduled_at.replace(minute=0, second=0, microsecond=0)

        cmd = Monitor(go_server, 'Run-After-Time', ran_after=scheduled_at.strftime('%H:%M'))
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._green_pipeline(scheduled_at=scheduled_at + timedelta(minutes=1))]
        )
        result = cmd.run()

        assert result['output'].startswith('OK: Successful')

    def test_determine_pipeline_has_run_after_given_time_in_the_past_failed(self, go_server):
        scheduled_at = datetime.now() - timedelta(hours=1)
        scheduled_at = scheduled_at.replace(minute=0, second=0, microsecond=0)

        cmd = Monitor(go_server, 'Run-After-Time', ran_after=scheduled_at.strftime('%H:%M'))
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._green_pipeline(scheduled_at=scheduled_at - timedelta(minutes=1))]
        )
        result = cmd.run()

        assert result['output'] == 'CRITICAL: Pipeline "{0}" has not run after "{1}".'.format(
            cmd.name,
            cmd._format_timestamp(cmd.ran_after)
        )

    def test_determine_pipeline_has_run_after_given_time_in_the_future(self, go_server):
        # This is to say we want it to run at 14:00 and it's currently 13:15, then it should be
        # check if it ran after that time since yesterday.
        scheduled_at = datetime.now() + timedelta(hours=1)
        scheduled_at = scheduled_at.replace(minute=0, second=0, microsecond=0)

        cmd = Monitor(go_server, 'Run-After-Time', ran_after=scheduled_at.strftime('%H:%M'))
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._green_pipeline(
                scheduled_at=scheduled_at - timedelta(hours=23, minutes=59, seconds=30)
            )]
        )
        result = cmd.run()

        assert result['output'].startswith('OK: Successful')

    def test_determine_pipeline_has_run_after_given_time_in_the_future_failed(self, go_server):
        # This should've run after the given time yesterday but hasn't
        scheduled_at = datetime.now() + timedelta(hours=1)
        scheduled_at = scheduled_at.replace(minute=0, second=0, microsecond=0)

        cmd = Monitor(go_server, 'Run-After-Time', ran_after=scheduled_at.strftime('%H:%M'))
        cmd.pipeline.history.return_value = dict(
            pipelines=[self._green_pipeline(
                scheduled_at=scheduled_at - timedelta(days=1, hours=2)
            )]
        )
        result = cmd.run()

        assert result['output'] == 'CRITICAL: Pipeline "{0}" has not run after "{1}".'.format(
            cmd.name,
            cmd._format_timestamp(cmd.ran_after)
        )
