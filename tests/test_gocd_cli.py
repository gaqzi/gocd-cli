import pytest
from mock import MagicMock

from gocd import Server
from gocd.api import Pipeline
import gocd_cli


@pytest.fixture
def args_positional():
    return ('pipeline', 'retrigger-failed', 'Simple-with-lock')


@pytest.fixture
def args():
    return (
        'pipeline',
        'retrigger-failed',
        'Simple-with-lock',
        '--stage=firstStage',
        '--retrigger',
        'stage',
    )


@pytest.fixture
def go_server():
    server = MagicMock(spec=Server)
    server.pipeline.return_value = MagicMock(spec=Pipeline)

    return server


def test_format_arguments():
    args, kwargs = gocd_cli.format_arguments(
        'name',
        '--stage=firstStage',
        '--retrigger',
        'stage',
        '--pipeline-name=Simple-with-lock',
        'some-other',
    )

    assert args == ['name', 'some-other']
    assert kwargs == {
        'stage': 'firstStage',
        'retrigger': 'stage',
        'pipeline_name': 'Simple-with-lock'
    }


def test_get_command_successfully_sets_all_args(args):
    go_server = Server('http://localhost:8153')
    command = gocd_cli.get_command(go_server, *args)

    assert command.pipeline.name == 'Simple-with-lock'
    assert command.stage == 'firstStage'
    assert command.retrigger_type == 'stage'


def test_get_command_raises_reasonable_errors(go_server):
    with pytest.raises(ImportError) as exc:
        gocd_cli.get_command(go_server, 'no-such-module', 'retrigger-failed')
    assert 'gocd_cli.commands:' in str(exc)

    with pytest.raises(AttributeError) as exc:
        gocd_cli.get_command(go_server, 'pipeline', 'no-such-command')
    assert 'gocd_cli.commands.pipeline' in str(exc)
    assert 'object has no attribute \'NoSuchCommand\'' in str(exc)

    with pytest.raises(TypeError) as exc:
        gocd_cli.get_command(go_server, 'pipeline', 'retrigger-failed')
    assert 'RetriggerFailed' in str(exc)
    assert '__init__() takes at least 3 arguments (2 given)' in str(exc)
