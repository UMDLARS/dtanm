import os
import tarfile

import pytest

from models.attack import extract_tar
from tests import get_test_resource


@pytest.fixture
def temp_dir():
    import tempfile
    import shutil
    dir_name = tempfile.mkdtemp()
    yield dir_name
    shutil.rmtree(dir_name)


def test_extract_tar_only_files(temp_dir):
    tarball = get_test_resource('tarball_tests', 'tar_files.tar.gz')
    with tarfile.open(tarball, "r") as tf:
        extract_tar(tf, temp_dir)
        for i in [1, 2, 3]:
            assert os.path.exists(os.path.join(temp_dir, f'file{i}'))
            assert open(os.path.join(temp_dir, f'file{i}'), 'r').read() == f'file{i}\n'