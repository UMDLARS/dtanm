from __future__ import unicode_literals

import pytest

from scorer.attack import parse_args

# This dict contains the input to the output excepted from attack_to_args
tests = {b"": [],
         b"0": [b"0"],
         b"\"\"": [b""],
         b"0 1 2": [b"0", b"1", b"2"], }


@pytest.mark.parametrize("attack,args", tests.items())
def test_parse_args(attack, args):
    assert parse_args(attack) == args
