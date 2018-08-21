from scorer.db import lpop_to_str
from .conn import redis_conn


def add_team(team_id: str):
    r = redis_conn()
    r.rpush('updates', f't-{team_id}')


def add_attack(attack_id: str):
    r = redis_conn()
    r.rpush('updates', f'a-{attack_id}')


def next_update(block=True) -> str:
    r = redis_conn()
    func = r.lpop
    if block:
        func = r.blpop
    return lpop_to_str(func('updates'))
