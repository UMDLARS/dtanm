from __future__ import unicode_literals

import os
import tarfile
from io import BytesIO
from tarfile import TarFile, TarInfo, DIRTYPE
from typing import Dict

import pytest

from scorer.manager import AttackManager, extract_tar
from tests import get_test_resource


@pytest.fixture
def temp_dir():
    import tempfile
    import shutil
    dir_name = tempfile.mkdtemp()
    yield dir_name
    shutil.rmtree(dir_name)


@pytest.fixture
def temp_attack_dir():
    import tempfile
    import shutil
    dir_name = tempfile.mkdtemp()
    yield dir_name
    shutil.rmtree(dir_name)


@pytest.fixture
def temp_upload_dir():
    import tempfile
    import shutil
    dir_name = tempfile.mkdtemp()
    yield dir_name
    shutil.rmtree(dir_name)


@pytest.fixture
def manager(temp_attack_dir, temp_upload_dir):
    return AttackManager(upload_dir=temp_upload_dir, attacks_dir=temp_attack_dir)


def create_attack(path, cmd_args: bytes, stdin: bytes, env_files: Dict[str, bytes] = None):
    with TarFile(path, mode="w") as tf:
        cmd_args_ti = TarInfo("cmd_args")
        cmd_args_ti.size = len(cmd_args)
        tf.addfile(cmd_args_ti, BytesIO(cmd_args))

        stdin_ti = TarInfo("stdin")
        stdin_ti.size = len(stdin)
        tf.addfile(stdin_ti, BytesIO(stdin))

        env_ti = TarInfo("env")
        env_ti.type = DIRTYPE
        tf.addfile(env_ti, None)

        if env_files:
            for path, data in env_files.items():
                ti = TarInfo(os.path.basename(path))
                ti.path = path
                ti.size = len(data)
                tf.addfile(ti, BytesIO(data))


def test_load_existing_attacks_no_attacks(manager):
    assert len(manager.load_existing_attacks()) == 0


def test_load_existing_attacks_one_attacks(manager):
    assert len(manager.load_existing_attacks()) == 0
    attack_name = "test_attack.tar.gz"
    create_attack(f"{manager.upload_dir}/{attack_name}", b"", b"")
    manager.process_attack(attack_name)

    assert len(manager.load_existing_attacks()) == 1


def test_process_attack(manager):
    assert len(manager.load_existing_attacks()) == 0
    attack_name = "test_attack.tar.gz"
    create_attack(f"{manager.upload_dir}/{attack_name}", b"", b"")

    attack = manager.process_attack(attack_name)
    assert attack is not None
    assert attack.exists()


def test_extract_tar_only_files(temp_dir):
    tarball = get_test_resource('tarball_tests', 'tar_files.tar.gz')
    with tarfile.open(tarball, "r") as tf:
        extract_tar(tf, temp_dir)
        for i in [1, 2, 3]:
            assert os.path.exists(os.path.join(temp_dir, f'file{i}'))
            assert open(os.path.join(temp_dir, f'file{i}'), 'r').read() == f'file{i}\n'


def test_extract_tar_single_dir(temp_dir):
    tarball = get_test_resource('tarball_tests', 'tar_test_dir.tar.gz')
    with tarfile.open(tarball, "r") as tf:
        extract_tar(tf, temp_dir)
        assert os.path.exists(os.path.join(temp_dir, 'dir1'))
        assert os.path.isdir(os.path.join(temp_dir, 'dir1'))


def test_extract_tar_single_dir_with_sub_files(temp_dir):
    tarball = get_test_resource('tarball_tests', 'tar_test_dir_files.tar.gz')
    with tarfile.open(tarball, "r") as tf:
        extract_tar(tf, temp_dir)
        assert os.path.exists(os.path.join(temp_dir, 'dir1'))
        assert os.path.isdir(os.path.join(temp_dir, 'dir1'))
        for i in [1, 2, 3]:
            assert os.path.exists(os.path.join(temp_dir, f'file{i}'))
            assert open(os.path.join(temp_dir, f'file{i}'), 'r').read() == f'file{i}\n'
        for i in [1, 2, 3]:
            assert os.path.exists(os.path.join(temp_dir, f'dir1/file{i}'))
            assert open(os.path.join(temp_dir, f'dir1/file{i}'), 'r').read() == f'file{i}\n'


def test_extract_tar_multiple_nested_dirs_with_sub_files(temp_dir):
    tarball = get_test_resource('tarball_tests', 'tar_test_dirs_files.tar.gz')
    with tarfile.open(tarball, "r") as tf:
        extract_tar(tf, temp_dir)
        for d in ['.', 'dir1', 'dir1/dir2', 'dir1/dir2/dir3']:
            assert os.path.exists(os.path.join(temp_dir, d))
            assert os.path.isdir(os.path.join(temp_dir, d))
            for i in [1, 2, 3]:
                assert os.path.exists(os.path.join(temp_dir, f'{d}/file{i}'))
                assert open(os.path.join(temp_dir, f'{d}/file{i}'), 'r').read() == f'file{i}\n'


# TODO: Add tests that test hashing, etc...
