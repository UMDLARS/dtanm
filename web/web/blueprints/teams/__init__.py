from flask import render_template, Blueprint
from flask_security import login_required, current_user
from web import db
from web.models.team import Team
from web.models.result import Result
from sqlalchemy.sql import text
from typing import List

teams = Blueprint('teams', __name__, template_folder='templates')

@teams.route('/')
def index():
    return render_template('teams/index.html', teams=Team.query.all())

def get_results_for_show_page(team_id: int) -> List[Result]:
    return db.session.query(Result).from_statement(
        text("""WITH results AS (
            SELECT r.*, ROW_NUMBER() OVER (PARTITION BY attack_id ORDER BY created_at DESC) AS rn
            FROM result as r
            ) SELECT * from results WHERE rn = 1 AND team_id = :team_id;
            """)
    ).params(team_id=team_id).all()

@teams.route('/<int:team_id>')
def show(team_id):
    team=Team.query.get_or_404(team_id)
    return render_template('teams/show.html', team=team, results=get_results_for_show_page(team_id))

@teams.route('/me')
@login_required
def me():
    return show(current_user.team_id)
