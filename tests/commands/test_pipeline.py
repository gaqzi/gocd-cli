import pytest
from mock import MagicMock

from gocd import Server
from gocd.api import Pipeline
from gocd_cli.commands.pipeline import Trigger, Unlock


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
        cmd.pipeline.schedule.assert_called_once_with()


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
