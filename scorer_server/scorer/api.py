from flask import Blueprint, abort
from flask import current_app as app

from scorer.tasker import get_task_queue, get_attack_manager
from scorer.tasks import AttackUpdate, TeamUpdate
from scorer.team import Team

bp = Blueprint('api', __name__)


@bp.route('/team/<team_name>')
def team_update(team_name):
    app.logger.debug(f"Team {team_name}'s code updated")
    team = Team(team_name)  # TODO: Verify that this is a good team.
    get_task_queue().put(TeamUpdate(team))
    return ""


@bp.route('/attack/<attack_name>')
def new_attack(attack_name):
    app.logger.debug(f"New Attack submitted: '{attack_name}'")
    attack = get_attack_manager().process_attack(attack_name)
    if not attack:  # If the attack was invalid.
        abort(400)

    get_task_queue().put(AttackUpdate(attack))
    return ""
