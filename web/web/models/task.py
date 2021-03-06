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

    Note that if a team submits their code to be scored, and then submits it
    again before the previous scoring finishes, any of the previous tasks of
    this team in the queue will be overwritten, as their content will be the
    same. This is good for us, as it allows us to score more quickly, and to
    minimize the length of time that a team's results are out of date.
    """
    if priority is None:
        priority = time()
    redis.zadd('tasks', {f'{team_id}-{attack_id}': str(priority)})


def get_task():
    return pop_to_str(redis.bzpopmin('tasks'))
