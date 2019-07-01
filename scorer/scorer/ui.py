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

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/scoring')
def show_scoreboard():
    return render_template('scoring.html')

@bp.route('/scoring/team/<int:team_id>')
def show_team_score(team_id):
    return render_template('team_score.html')

@bp.route('/attacks')
def attacks():
    return render_template('attacks.html')
