from scorer.db import spop_to_str
from .conn import redis_conn


def add_task(team_id: str, attack_id: str, priority: float=None):
    """
    Args:
        priority: NOTE: THIS IS NOT IMPLEMENTED. We are waiting for redis v5.
    """
    r = redis_conn()
    r.sadd('tasks', f'{team_id}-{attack_id}')


def get_task(block=False):
    assert not block, "Currently blocking isn't implemented."
    r = redis_conn()
    return spop_to_str(r.spop('tasks'))
