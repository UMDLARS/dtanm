from flask import render_template, Blueprint, redirect, request, flash
from flask_security import login_required, current_user
from web import db, team_required, formatters
from web.models.team import Team
from web.models.result import Result
from sqlalchemy.sql import text
from typing import List

teams = Blueprint('teams', __name__, template_folder='templates')

@teams.route('/')
def index():
    teams=Team.query.all()
    teams.sort(key=lambda team: len(team.passing), reverse=True)
    return render_template('teams/index.html', teams=teams)

@teams.route('/table')
def index_table():
    teams=Team.query.all()
    teams.sort(key=lambda team: len(team.passing), reverse=True)
    return render_template('teams/index_table.html', teams=teams)

@teams.route('/<int:team_id>')
def show(team_id):
    """Show the passing/failing attacks of team `team_id`. Optionally can be
       passed a hash in the URI such as `#row123` to highlight result #123
       (useful for example when coming from an attack page)."""
    team=Team.query.get_or_404(team_id)
    return render_template('teams/show.html', team=team, formatters=formatters)

@teams.route('/<int:team_id>/table')
def show_table(team_id):
    team=Team.query.get_or_404(team_id)
    return render_template('teams/show_table.html', team=team)

@teams.route('/me')
@login_required
@team_required
def me():
    return show(current_user.team_id)
