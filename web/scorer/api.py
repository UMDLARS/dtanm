from flask import Blueprint, abort, jsonify, request, flash, redirect, url_for
from flask import current_app as app
from werkzeug.utils import secure_filename
import os

from scorer.db.conn import connect_mongo
from scorer.db.result import Result
from scorer.db.update import add_team, add_attack
from scorer.manager import get_attack_manager, get_team_manager

bp = Blueprint('api', __name__)


@bp.before_app_first_request
def connect_to_mongo():
    pass # connect_mongo()


@bp.route('/team/<team_name>')
def team_update(team_name):
    app.logger.debug(f"Code update for team: '{team_name}'")
    team = get_team_manager().process_team(team_name)
    if not team:  # If the team was invalid.
        abort(400)

    add_team(team.id)
    return jsonify(id=team.id)

@bp.route('/attacks', methods=["POST"])
def upload_attack_tar():
    # check if the post request has the file part
    if 'attack' not in request.files:
        return 'No file part'
    attack = request.files['attack']
    # if user does not select file, browser also
    # submit an empty part without filename
    if attack.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if attack:
        filename = secure_filename(attack.filename)
        attack.save(os.path.join(app.config['UPLOAD_DIR'], filename))
        app.logger.debug(f"New Attack submitted: '{filename}'")
        attack = get_attack_manager().process_attack(filename)
    else:  # If the attack was invalid.
        abort(400)

    add_attack(attack.id)
    return jsonify(id=attack.id)


@bp.route('/results')
def get_results():
    app.logger.debug(f'Got results request')
    return Result.objects.to_json()


@bp.route('/')
def index():
    return "Hi."
