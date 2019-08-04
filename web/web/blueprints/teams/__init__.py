from flask import render_template, Blueprint
from flask_security import login_required, current_user
from web import db
from web.models.team import Team

teams = Blueprint('teams', __name__, template_folder='templates')

@teams.route('/')
def index():
    return render_template('teams/index.html', teams=Team.query.all())

@teams.route('/<int:team_id>')
def show(team_id):
    team=Team.query.get_or_404(team_id)
    return render_template('teams/show.html', team=team)

@teams.route('/me')
@login_required
def me():
    return render_template('teams/show.html', team=current_user.team)
