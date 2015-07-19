import pytest

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


def test_format_arguments():
    args, kwargs = gocd_cli.format_arguments([
        'name',
        '--stage=firstStage',
        '--retrigger',
        'stage',
        'some-other',
    ])

    assert args == ['name', 'some-other']
    assert kwargs == {'stage': 'firstStage', 'retrigger': 'stage'}
