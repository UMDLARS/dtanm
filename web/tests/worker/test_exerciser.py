import tempfile
from pathlib import PosixPath
from unittest.mock import MagicMock

import pytest

from scorer.worker import Exerciser
from tests import get_test_resource


@pytest.fixture
def empty_stdin():
    with tempfile.NamedTemporaryFile() as tf:
        yield tf.name


@pytest.fixture(scope="function",
                params=[False, True],
                ids=["without env", "with env"])
def mock_attack(empty_stdin, setup_env=False):
    with tempfile.TemporaryDirectory() as temp_env_dir:
        attack = MagicMock()
        attack.stdin_filepath = empty_stdin
        attack.cmd_args = []
        attack.env = None
        if setup_env:
            attack.env = temp_env_dir
        yield attack


@pytest.mark.parametrize("newline", [True, False], ids=["with trailing newline", "without trailing newline"])
@pytest.mark.parametrize("args, output", [
    ([b"Hi"], b"Hi"),
    ([b"Hi\nTest"], b"Hi\nTest"),
    ([b"-e", b"Hi\\nTest"], b"Hi\nTest"),
    ([b"-E", b"Hi\\nTest"], b"Hi\\nTest"),
])
def test_exerciser_echo_test(mock_attack, newline, args, output):
    flags = [] if newline else [b"-n"]
    mock_attack.cmd_args = flags + args
    with Exerciser("echo", mock_attack, src_path=get_test_resource('echo')) as ex:
        res = ex.run()
        assert res.stdout == output + (b"\n" if newline else b"")


def test_exerciser_setup_git_repo(mock_attack):
    with Exerciser(None, mock_attack, git_remote=get_test_resource('empty_repo')) as ex:
        assert PosixPath(ex.working_dir).exists()
        assert PosixPath(ex.source_dir).exists()

        if mock_attack.env:
            # Check if the env file was copied
            assert PosixPath(ex.working_dir, "env").exists()

        # Check if the source code is checked out.
        assert PosixPath(ex.source_dir, "empty").exists()

    # Check that everything is cleaned up
    assert not PosixPath(ex.working_dir).exists()
    assert not PosixPath(ex.source_dir).exists()
    assert not PosixPath(ex.working_dir, "env").exists()
    assert not PosixPath(ex.source_dir, "empty").exists()


def test_exerciser_setup_source_dir(mock_attack):
    with Exerciser(None, mock_attack, src_path=get_test_resource('empty_repo')) as ex:
        assert PosixPath(ex.working_dir).exists()
        assert PosixPath(ex.source_dir).exists()

        if mock_attack.env:
            # Check if the env file was copied
            assert PosixPath(ex.working_dir, "env").exists()

        # Check if the source code is checked out.
        assert PosixPath(ex.source_dir, "empty").exists()

    # Check that everything is cleaned up exist of course the source directory.
    assert not PosixPath(ex.working_dir).exists()
    assert not PosixPath(ex.working_dir, "env").exists()


def test_get_git_checksum(mock_attack):
    with Exerciser(None, mock_attack, git_remote=get_test_resource('empty_repo')) as exeriser:
        assert exeriser.get_repo_checksum() == '15b54584269476b7abde2f7e1db660a495069b12'
