from .conn import redis_conn


def add_team(team_id: str):
    r = redis_conn()
    r.rpush('updates', f't-{team_id}')


def add_attack(attack_id: str):
    r = redis_conn()
    r.rpush('updates', f'a-{attack_id}')


def next_update(block=True):
    r = redis_conn()
    if block:
        return r.blpop('updates')[1].decode("utf-8")
    return r.lpop('updates')[1].decode("utf-8")

