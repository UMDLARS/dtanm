from queue import Queue

import pytest
from mock import patch

from scorer.tasker import Tasker
from scorer.tasks import AttackUpdate, TeamUpdate, ScoreTask


def a(n):
    return AttackUpdate(n)


def t(n):
    return TeamUpdate(n)


def s(team, attack):
    return ScoreTask(team=team, attack=attack)


@pytest.fixture
def tasker_builder():
    with patch('scorer.tasker.current_app') as current_app:
        def make_tasker(timeout=0.1, worker_count=1):
            current_app.config = {"TASKER_LOOP_TIMEOUT_SEC": timeout,
                                  "WORKER_COUNT": worker_count}
            return Tasker(queue=Queue())

        yield make_tasker


def test_process_in_queue_none(tasker):
    assert not tasker.process_in_queue()


@pytest.mark.parametrize('updates, buffered_tasks', [
    ([a(1)], []),
    ([t(1)], []),
    ([a(1), t(2)], [s(2, 1)]),
    ([a(1), t(2), a(3)], [s(2, 1), s(2, 3)]),
    ([a(1), t(2), a(3), t(4)], [s(2, 1), s(2, 3), s(4, 1), s(4, 3)]),
    ([t(1), t(2), a(3), a(4), a(5)], [s(x, y) for x in (1, 2) for y in (3, 4, 5)])
])
def test_process_in_queue(updates, buffered_tasks, tasker_builder):
    tasker = tasker_builder()
    for e in updates:
        tasker.in_queue.put(e)
    while tasker.process_in_queue():
        pass
    assert len(tasker.tasks) == len(buffered_tasks)
    for task in buffered_tasks:
        assert task in tasker.tasks
    assert tasker.out_queue.qsize() == 0


@pytest.mark.parametrize('before_buffered_tasks, thread_count, after_buffered_tasks, out_tasks', [
    ([], 1, [], []),
    ([s(2, 1)], 1, [], [s(2, 1)]),
    ([s(2, 1), s(2, 3)], 1, [s(2, 3)], [s(2, 1)]),
    ([s(2, 1), s(2, 3)], 2, [], [s(2, 1), s(2, 3)]),
    ([s(2, 1), s(2, 3), s(4, 1), s(4, 3)], 1, [s(2, 3), s(4, 1), s(4, 3)], [s(2, 1)]),
    ([s(2, 1), s(2, 3), s(4, 1), s(4, 3)], 3, [s(4, 3)], [s(2, 1), s(2, 3), s(4, 1)]),
    ([s(2, 1), s(2, 3), s(4, 1), s(4, 3)], 4, [], [s(2, 1), s(2, 3), s(4, 1), s(4, 3)]),
    *[([s(x, y) for x in (1, 2) for y in (3, 4, 5)], z + 1, [s(x, y) for x in (1, 2) for y in (3, 4, 5)][z + 1:],
       [s(x, y) for x in (1, 2) for y in (3, 4, 5)][0:z + 1]) for z in range(2 * 3)]
])
def test_process_out_queue(before_buffered_tasks, thread_count, after_buffered_tasks, out_tasks, tasker_builder):
    tasker = tasker_builder(worker_count=thread_count)
    for e in before_buffered_tasks:
        tasker.tasks.append(e)
    while tasker.update_out_queue():
        pass
    assert len(tasker.tasks) == len(after_buffered_tasks)
    for expected_task, task in zip(after_buffered_tasks, tasker.tasks):
        assert expected_task == task
    assert tasker.out_queue.qsize() == len(out_tasks)
    for task in out_tasks:
        assert tasker.out_queue.get() == task
