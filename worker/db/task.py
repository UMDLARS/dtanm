from time import time

from db import pop_to_str
from .conn import redis_conn


def add_task(team_id: str, attack_id: str, priority: float=None):
    """
    Args:
        priority: The lowest priority is picked first. Defaults to the current time.
    """
    r = redis_conn()
    if priority is None:
        priority = time()
    r.zadd('tasks', {f'{team_id}-{attack_id}': str(priority)})


def get_task():
    r = redis_conn()
    return pop_to_str(r.bzpopmin('tasks'))
