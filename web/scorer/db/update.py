from scorer.db import pop_to_str
from .conn import redis_conn


def add_team(team_id: str):
    r = redis_conn()
    r.rpush('updates', f't-{team_id}')


def add_attack(attack_id: str):
    r = redis_conn()
    r.rpush('updates', f'a-{attack_id}')


def next_update() -> str:
    r = redis_conn()
    return pop_to_str(r.blpop('updates'))
