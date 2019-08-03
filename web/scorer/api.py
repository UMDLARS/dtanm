from flask import Blueprint, abort, jsonify, request, flash, redirect, url_for
from flask import current_app as app
from werkzeug.utils import secure_filename
import os

from scorer.db.conn import connect_mongo, redis_conn
from scorer.db.result import Result
from scorer.db.task import add_task
from scorer.manager import get_attack_manager, get_team_manager
from mongoengine.connection import _get_db

bp = Blueprint('api', __name__)

redis=None


@bp.before_app_first_request
def connect_to_mongo():
    global redis
    redis=redis_conn()
    pass # connect_mongo()

def add_team(team_id):
    redis.sadd('teams', team_id)
    for attack_id in redis.smembers('attacks'):
        add_task(team_id, attack_id.decode('utf-8'))

def add_attack(attack_id):
    redis.sadd('attacks', attack_id)
    for team_id in redis.smembers('teams'):
        add_task(team_id.decode('utf-8'), attack_id)

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
    return jsonify(Result.objects)

@bp.route('/')
def index():
    return "Hi."

@bp.route('/reset')
def reset():
    if os.environ.get('ENVIRONMENT') != "dev":
        return "Cannot reset outside of dev mode"
    else:
        redis.flushall()
        db = _get_db()
        Result.drop_collection()
        return "okay"
