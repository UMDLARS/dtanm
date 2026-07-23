from time import time

from web import redis
from web.models.attack import AttackType

def pop_to_str(res):
    print(f"Got res: '{res}'")
    if res is not None and len(res) >= 2:
        if res[1] is not None:
            return res[1].decode('utf-8')
    return None

    """
    Args:
        priority: The lowest priority is picked first. Defaults to the current time.

    Note that if a team submits their code to be scored, and then submits it
    again before the previous scoring finishes, any of the previous tasks of
    this team in the queue will be overwritten, as their content will be the
    same. This is good for us, as it allows us to score more quickly, and to
    minimize the length of time that a team's results are out of date.
    """

def add_score_gold_task(attack_id: str, attack_type: int, priority: float=None):
    if priority is None:
        priority = time()
    if attack_type == AttackType.SCORE:
        redis.zadd('tasks', {f'a.{attack_id}': str(priority)})
    else:
        assert(attack_type == AttackType.SCORE_GOLD)
        redis.zadd('tasks', {f'g.{attack_id}': str(priority)})

def add_team_score_task(team_id: int, attack_id: int, priority: float=None):
    if priority == None:
        priority = time()
    redis.zadd('tasks', {f"t.{team_id}-{attack_id}": priority} )

def get_task():
    return pop_to_str(redis.bzpopmin('tasks'))
