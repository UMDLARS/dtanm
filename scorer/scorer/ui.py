from flask import Blueprint, abort, jsonify, render_template
from flask import current_app as app

from scorer.db.conn import connect_mongo
from scorer.db.result import Result
from scorer.db.update import add_team, add_attack
from scorer.manager import get_attack_manager, get_team_manager

bp = Blueprint('ui', __name__)


@bp.before_app_first_request
def connect_to_mongo():
    connect_mongo()


@bp.route('/team/<team_name>')
def team_update(team_name):
    app.logger.debug(f"Code update for team: '{team_name}'")
    team = get_team_manager().process_team(team_name)
    if not team:  # If the team was invalid.
        abort(400)

    add_team(team.id)
    return jsonify(id=team.id)


@bp.route('/attack/<attack_name>')
def new_attack(attack_name):
    app.logger.debug(f"New Attack submitted: '{attack_name}'")
    attack = get_attack_manager().process_attack(attack_name)
    if not attack:  # If the attack was invalid.
        abort(400)

    add_attack(attack.id)
    return jsonify(id=attack.id)


@bp.route('/results')
def get_results():
    app.logger.debug(f'Got results request')
    return Result.objects.to_json()


@bp.route('/')
def index():
    return render_template('index.html')
