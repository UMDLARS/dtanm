from flask import Blueprint, render_template, request, flash
from flask_security import login_required

from web.models.result import Result
from web.models.attack import Attack
from web.models.team import Team
from web.scorer.manager import get_attack_manager, get_team_manager

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@ui_bp.route('/submit_program')
@login_required
def submit_program():
    flash("This page has not yet been implemented and does not yet do anything.", category="warning")
    from urllib.parse import urlparse
    hostname=urlparse(request.url_root).hostname
    return render_template('submit_program.html', hostname=hostname)

@ui_bp.route('/gold')
@login_required
def test_against_gold():
    flash("This page has not yet been implemented and does not yet do anything.", category="warning")
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
    flash("This page has not yet been implemented and does not yet do anything.", category="warning")
    return render_template('stats.html', stats=gen_stats())

@ui_bp.route('/stats.json')
def json_stats():
    return gen_stats()