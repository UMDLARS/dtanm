import pytest
from io import StringIO
from manager import get_attack_from_file


# def test_empty_attack_file():
#     assert get_attack_from_file(StringIO("")) == "\n"

# This dict contains the input to the output excepted from get_attack_from_file
tests = {"": "\n",
         "Hey there\ntesting\nblA": "Hey there\n",}


@pytest.mark.parametrize("file_contents,attack", tests.items())
def test_get_attack_from_file(file_contents, attack):
    assert get_attack_from_file(StringIO(file_contents)) == attack

