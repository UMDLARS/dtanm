import pytest
from testprog import attack_to_args


# This dict contains the input to the output excepted from attack_to_args
tests = {"": [],
         "0": ["0"],
         "\"\"": [""],
         "0 1 2": ["0", "1", "2"],}


@pytest.mark.parametrize("attack,args", tests.items())
def test_attack_to_args(attack, args):
    assert attack_to_args(attack) == args
