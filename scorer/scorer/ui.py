from flask import Blueprint, abort, jsonify, render_template, request, url_for
from flask import current_app as app
from flask_security import login_required

from scorer.db.conn import connect_mongo
from scorer.db.result import Result
from scorer.db.update import add_team, add_attack
from scorer.manager import get_attack_manager, get_team_manager

ui_bp = Blueprint('ui', __name__)


@ui_bp.before_app_first_request
def connect_to_mongo():
    pass # connect_mongo()

@ui_bp.before_request
@login_required
def before_request():
    """ Protect all of the login-required endpoints. """
    pass 

@ui_bp.context_processor
def utility_processor():
    def create_menu_item(title: str, route_name: str):
        """
        Creates HTML for sidebar menu item, and highlights it if active

        Parameters:
            title (str): The displayed text of the menu item
            route_name (str): the Python path to the route (e.g. 'ui.index')
        """
        selected_class = "active" if request.path == url_for(route_name) else "bg-light"
        return f"<a href=\"{ url_for(route_name) }\" class=\"list-group-item list-group-item-action { selected_class }\">{title}</a>" 
    return dict(create_menu_item=create_menu_item)

@ui_bp.route('/')
def index():
    return render_template('index.html')

@ui_bp.route('/scoring')
def scoring():
    return render_template('scoring.html')

@ui_bp.route('/rankings')
def rankings():
    return render_template('rankings.html')

@ui_bp.route('/challenge')
def challenge():
    return render_template('challenge.html')

@ui_bp.route('/scoring/teams/<int:team_id>')
def show_team_score(team_id):
    return render_template('team_score.html')

@ui_bp.route('/submit_attack')
def submit_attack():
    return render_template('submit_attack.html')

@ui_bp.route('/submit_program')
def submit_program():
    return render_template('submit_program.html')

@ui_bp.route('/gold')
def test_against_gold():
    return render_template('test_against_gold.html')

@ui_bp.route('/stats')
def stats():
    return render_template('stats.html')

