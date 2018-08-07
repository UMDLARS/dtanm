from __future__ import unicode_literals

import os
from io import BytesIO
from tarfile import TarFile, TarInfo, DIRTYPE
from typing import Dict

import pytest

from scorer.manager import AttackManager


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

# TODO: Add tests that test hashing, etc...
