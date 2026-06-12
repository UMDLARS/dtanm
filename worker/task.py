from redis import Redis
from time import time
import os
from run_worker import redis

def add_team_score_task(team_id: str, attack_id: str, priority: float=None):
    if priority == None:
        priority = time()
    redis.zadd('tasks', {f"t.{team_id}-{attack_id}": priority} )

