from .conn import redis_conn


def add_task(team_id: str, attack_id: str, priority: float=None):
    """
    Args:
        priority: NOTE: THIS IS NOT IMPLEMENTED. We are waiting for redis v5.
    """
    r = redis_conn()
    r.sadd('tasks', f'{team_id}-{attack_id}')


