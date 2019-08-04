from flask import Blueprint, abort, jsonify, render_template, request, url_for
from flask import current_app as app
from flask_security import login_required

from web.scorer.db.conn import connect_mongo
from web.scorer.db.result import Result
from web.scorer.manager import get_attack_manager, get_team_manager

ui_bp = Blueprint('ui', __name__)


@ui_bp.before_app_first_request
def connect_to_mongo():
    pass # connect_mongo()

@ui_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@ui_bp.route('/scoring')
@login_required
def scoring():
    return render_template('scoring.html', scores=Result.objects)

@ui_bp.route('/rankings')
def rankings():
    return render_template('rankings.html')

@ui_bp.route('/scoring/teams/<int:team_id>')
@login_required
def show_team_score(team_id):
    return render_template('team_score.html')

@ui_bp.route('/submit_attack')
@login_required
def submit_attack():
    return render_template('submit_attack.html')

@ui_bp.route('/submit_program')
@login_required
def submit_program():
    from urllib.parse import urlparse
    hostname=urlparse(request.url_root).hostname
    return render_template('submit_program.html', hostname=hostname)

@ui_bp.route('/gold')
@login_required
def test_against_gold():
    return render_template('test_against_gold.html')

def gen_stats():
    return {
        "Teams competing": "3",
        "Attacks submitted": "42",
        "Average score time": "3521ms",
        "Attacks in scoring queue": "0",
        "Scoring workers": "8",
        "Idle scoring workers": "6",
    }

@ui_bp.route('/stats')
def stats():
    return render_template('stats.html', stats=gen_stats())

@ui_bp.route('/stats.json')
def json_stats():
    return gen_stats()