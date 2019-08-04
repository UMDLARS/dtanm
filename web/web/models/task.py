from time import time

from web import redis

def pop_to_str(res):
    print(f"Got res: '{res}'")
    if res is not None and len(res) >= 2:
        if res[1] is not None:
            return res[1].decode('utf-8')
    return None


def add_task(team_id: str, attack_id: str, priority: float=None):
    """
    Args:
        priority: The lowest priority is picked first. Defaults to the current time.
    """
    if priority is None:
        priority = time()
    redis.zadd('tasks', {f'{team_id}-{attack_id}': str(priority)})


def get_task():
    return pop_to_str(redis.bzpopmin('tasks'))
