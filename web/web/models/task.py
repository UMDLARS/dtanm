from time import time

from web import redis
import json

def add_task(team_id: str, attack_id: str, priority: float=None, additional_data=None):
    """
    Args:
        priority: The lowest priority is picked first. Defaults to the current time.
        additional_data: Extra information that's passed through to the scoring worker.

    Info that we're currently passing through additional_data includes:
        existing_result: the id of a Result to use, rather than creating a new
            one. This is used for testing against gold, where we want to know
            the id of the Result before it runs, so that we can redirect the
            user to the right page.
        force_fail: This is a hack for type=test runs. Because Formatters only
            display output that the team's code produced incorrectly, this tells
            the worker to pretend that the result was wholly incorrect, so that
            the full output is always displayed by the Formatter.

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
