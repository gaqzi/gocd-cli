import pytest
import time
from datetime import datetime, timedelta
from gocd import Server
from gocd.api import Pipeline
from mock import MagicMock
from gocd.api.response import Response
from gocd_cli.commands.pipeline import Check, Pause, Trigger, Unlock, Unpause


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
        cmd.pipeline.schedule.assert_called_once_with(
            variables=None,
            secure_variables=None,
            return_new_instance=False
        )

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
            secure_variables=None,
            return_new_instance=False,
        )

    def test_trigger_with_secure_variables(self, go_server):
        cmd = Trigger(go_server, 'Moria', secure_variables='PASSCODE=Mellon')
        cmd.run()

        cmd.pipeline.schedule.assert_called_once_with(
            variables=None,
            secure_variables=dict(PASSCODE='Mellon'),
            return_new_instance=False,
        )

# I'll do this in integration instead
# class TestTriggerAndWaitUntilFinished(object):
#     def test_triggers_pipeline_and_waits_until_all_stages_have_finished(self, go_server):
#         cmd = Trigger(go_server, 'Simple-Pipeline', wait_until_finished=True)
#         output = cmd.run()
#
#         go_server.pipeline.assert_called_once_with('Simple-Pipeline')
#         cmd.pipeline.schedule.assert_called_once_with(
#             variables=None,
#             secure_variables=None,
#             return_new_instance=True
#         )
#
#         assert output['exit_code'] == 0
#         assert output['output'] == "I'm so output, I'll blow your mind"


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
    @pytest.fixture(autouse=True)
    def setup(self, go_server):
        self.go_server = go_server

    def _pipeline(self, result='Unknown', job_state='Scheduled', scheduled_minutes_back=20):
        scheduled_date = time.time() - (60 * (scheduled_minutes_back or 20))

        return Response._from_json({
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
        })

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

    def _check(self, pipeline_name, pipeline, **kwargs):
        cmd = Check(self.go_server, pipeline_name, **kwargs)
        cmd.pipeline.status.return_value = dict(paused=False)  # XXX: is this a bad idea?
        cmd.pipeline.instance.return_value = pipeline
        return cmd

    def _snap_to_hour(self, timestamp):
        return timestamp.replace(minute=0, second=0, microsecond=0)

    def _assert_ok(self, cmd):
        assert cmd.run()['output'].startswith('OK: Successful')

    def test_determines_pipeline_has_stalled_warning(self):
        cmd = self._check(
            'Stalled-Pipeline',
            self._scheduled_pipeline(),
            warn_run_time=10
        )
        result = cmd.run()

        assert result['output'].startswith('WARNING: Pipeline "Stalled-Pipeline" stalled at')
        assert result['exit_code'] == 1

    def test_determines_pipeline_has_stalled_critical(self):
        cmd = self._check(
            'Stalled-Pipeline',
            self._scheduled_pipeline(scheduled_minutes_back=20),
            warn_run_time=10,
            crit_run_time=15
        )
        result = cmd.run()

        assert result['output'].startswith('CRITICAL: Pipeline "Stalled-Pipeline" stalled at')
        assert result['exit_code'] == 2

    def test_determines_pipeline_is_successful(self):
        cmd = self._check('Green-Pipeline', self._green_pipeline())
        result = cmd.run()

        assert result['output'] == 'OK: Successful'
        assert result['exit_code'] == 0

    def test_determine_pipeline_is_failed(self):
        cmd = self._check('Red-Pipeline', self._red_pipeline())
        result = cmd.run()

        assert result['output'].startswith('CRITICAL: Pipeline "Red-Pipeline" failed')
        assert result['exit_code'] == 2

    def test_pipeline_is_building(self):
        """
        When pipeline state isn't Passed or Failed the pipeline should
        be assumed to be in progress.
        """
        self._assert_ok(self._check('Currently-Building', self._building_pipeline()))

    def test_pipeline_is_building_and_has_stages_that_arent_scheduled(self):
        cmd = self._check(
            'Currently-Building',
            self._running_pipeline_with_unscheduled_stage()
        )
        self._assert_ok(cmd)

    def test_now_is_in_milliseconds(self):
        cmd = self._check('Whatever', self._green_pipeline())

        assert (cmd._now - time.time()) >= 1000

    def test_determine_pipeline_has_run_after_given_time_in_the_past(self):
        scheduled_at = self._snap_to_hour(datetime.now() - timedelta(hours=1))

        cmd = self._check(
            'Run-After-Time',
            self._green_pipeline(scheduled_at=scheduled_at + timedelta(minutes=1)),
            ran_after=scheduled_at.strftime('%H:%M')
        )
        self._assert_ok(cmd)

    def test_determine_pipeline_has_run_after_given_time_in_the_future(self):
        # This is to say we want it to run at 14:00 and it's currently 13:15, then it should be
        # check if it ran after that time since yesterday.
        scheduled_at = self._snap_to_hour(datetime.now() + timedelta(hours=1))

        cmd = self._check(
            'Run-After-Time',
            self._green_pipeline(
                scheduled_at=scheduled_at - timedelta(hours=23, minutes=59, seconds=30)
            ),
            ran_after=scheduled_at.strftime('%H:%M')
        )
        self._assert_ok(cmd)

    def _assert_critical_run_after(self, cmd):
        result = cmd.run()
        assert result['output'] == 'CRITICAL: Pipeline "{0}" has not run after "{1}".'.format(
            cmd.name,
            cmd._format_timestamp(cmd.ran_after)
        )

    def test_determine_pipeline_has_run_after_given_time_in_the_past_failed(self):
        scheduled_at = self._snap_to_hour(datetime.now() - timedelta(hours=1))

        cmd = self._check(
            'Run-After-Time',
            self._green_pipeline(scheduled_at=scheduled_at - timedelta(minutes=1)),
            ran_after=scheduled_at.strftime('%H:%M')
        )

        self._assert_critical_run_after(cmd)

    def test_determine_pipeline_has_run_after_given_time_in_the_future_failed(self):
        # This should've run after the given time yesterday but hasn't
        scheduled_at = self._snap_to_hour(datetime.now() + timedelta(hours=1))

        cmd = self._check(
            'Run-After-Time',
            self._green_pipeline(scheduled_at=scheduled_at - timedelta(days=1, hours=2)),
            ran_after=scheduled_at.strftime('%H:%M')
        )

        self._assert_critical_run_after(cmd)

    def test_sets_state_to_unknown_when_pipeline_is_paused(self):
        cmd = self._check('Paused', self._green_pipeline())
        cmd.pipeline.status.return_value = dict(paused=True)
        result = cmd.run()

        assert result['exit_code'] == 3
        assert result['output'] == 'UNKNOWN: Pipeline "{0}" is paused'.format(cmd.name)

    def test_no_instances_of_pipeline_run_yet_and_ran_after_is_none(self):
        cmd = self._check('Never-Run', Response._from_json({}))

        assert cmd.run()['output'].startswith('OK: No scheduled runs')

    def test_no_instances_of_pipeline_run_yet_and_ran_after_is_set(self):
        cmd = self._check('Never-Run', Response._from_json({}), ran_after='18:00')

        self._assert_critical_run_after(cmd)
