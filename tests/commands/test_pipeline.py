import pytest
from mock import MagicMock

from gocd import Server
from gocd.api import Pipeline
from gocd_cli.commands.pipeline import Pause, Trigger, Unlock, Unpause


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
        cmd.pipeline.schedule.assert_called_once_with(variables=None)

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
            variables=dict(PIPELINE='The-Matrix')
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


class TestPause(object):
    def test_pauses_when_unpaused(self, go_server):
        cmd = Pause(go_server, 'Simple-Pipeline')
        cmd.pipeline.status.return_value = dict(paused=False)
        cmd.run()

        cmd.pipeline.pause.assert_called_with()

    def test_doesnt_run_if_already_paused(self, go_server):
        cmd = Pause(go_server, 'Simple-Pipeline')
        cmd.pipeline.status.return_value = dict(paused=True)
        cmd.run()

        assert not cmd.pipeline.pause.called


class TestUnpause(object):
    def test_unpauses_when_paused(self, go_server):
        cmd = Unpause(go_server, 'Simple-Pipeline')
        cmd.pipeline.status.return_value = dict(paused=True)
        cmd.run()

        cmd.pipeline.unpause.assert_called_with()

    def test_doesnt_run_if_already_unpaused(self, go_server):
        cmd = Unpause(go_server, 'Simple-Pipeline')
        cmd.pipeline.status.return_value = dict(paused=False)
        cmd.run()

        assert not cmd.pipeline.unpause.called
