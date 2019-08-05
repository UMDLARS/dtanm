from flask import Blueprint, abort, jsonify, request, flash, redirect, url_for
from flask import current_app as app
import os

from web.models.result import Result

from web.scorer.manager import get_attack_manager, get_team_manager

bp = Blueprint('api', __name__)

from web import redis

def add_team(team_id):
    redis.sadd('teams', team_id)
    for attack_id in redis.smembers('attacks'):
        add_task(team_id, attack_id.decode('utf-8'))

def add_attack(attack_id):
    redis.sadd('attacks', attack_id)
    for team_id in redis.smembers('teams'):
        add_task(team_id.decode('utf-8'), attack_id)

@bp.route('/team/<team_name>')
def team_update(team_name):
    app.logger.debug(f"Code update for team: '{team_name}'")
    team = get_team_manager().process_team(team_name)
    if not team:  # If the team was invalid.
        abort(400)

    add_team(team.id)
    return jsonify(id=team.id)
