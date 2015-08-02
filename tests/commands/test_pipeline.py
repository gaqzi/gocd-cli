import pytest
from mock import MagicMock

from gocd import Server
from gocd.api import Pipeline
from gocd_cli.commands.pipeline import Trigger


@pytest.fixture
def go_server():
    server = MagicMock(spec=Server)
    server.pipeline.return_value = MagicMock(spec=Pipeline)

    return server


@pytest.fixture
def trigger_command(go_server):
    return Trigger(go_server, 'Simple-Pipeline')


class TestTrigger(object):
    def test_triggers_the_named_pipeline(self, go_server):
        t = Trigger(go_server, 'Simple-Pipeline')
        t.run()

        go_server.pipeline.assert_called_once_with('Simple-Pipeline')
        t.pipeline.schedule.assert_called_once_with()
