from queue import Queue

import pytest
from mock import patch, Mock

from scorer.tasker import Tasker
from scorer.tasks import AttackUpdate, TeamUpdate, ScoreTask


def a(n):
    return f'a-{n}'


def t(n):
    return f't-{n}'


def s(team, attack):
    return str(team), str(attack)


@pytest.fixture
def tasker():
    return Tasker()


@patch('scorer.tasker.add_task')
def test_process_none(add_task: Mock, tasker):
    assert not tasker._process_update(None)
    add_task.assert_not_called()


@pytest.mark.parametrize('updates, tasks', [
    ([a(1)], []),
    ([t(1)], []),
    ([a(1), t(2)], [s(2, 1)]),
    ([a(1), t(2), a(3)], [s(2, 1), s(2, 3)]),
    ([a(1), t(2), a(3), t(4)], [s(2, 1), s(2, 3), s(4, 1), s(4, 3)]),
    ([t(1), t(2), a(3), a(4), a(5)], [s(x, y) for x in (1, 2) for y in (3, 4, 5)])
])
@patch('scorer.tasker.add_task')
def test_process(add_task: Mock, updates, tasks, tasker):
    for e in updates:
        tasker._process_update(e)

    assert add_task.call_count == len(tasks)
    for task in tasks:
        add_task.assert_any_call(*task)
