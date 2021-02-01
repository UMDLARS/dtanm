from time import time

from web import redis
import json

def add_task(team_id: str, attack_id: str, priority: float=None, additional_data=None):
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

    data = {
        "team_id": team_id,
        "attack_id": attack_id
    }
    if additional_data:
        data.update(additional_data)

    # Sort keys makes sure we don't have deduplication issues where, say,
    # {team_id: 1, attack_id: 1} != {attack_id: 1, team_id: 1}
    redis.zadd('tasks', {json.dumps(data, sort_keys=True): str(priority)})
