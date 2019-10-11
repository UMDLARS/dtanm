from flask import render_template, Blueprint, flash, request, url_for, redirect, send_from_directory, current_app
from flask_security import login_required, current_user
from web.models.attack import Attack, create_attack_from_post, create_attack_from_tar
from werkzeug.utils import secure_filename
from web.models.task import add_task
from web import db, team_required
import os
from web.models.team import Team
import datetime
from sqlalchemy import and_

attacks = Blueprint('attacks', __name__, template_folder='templates')

@attacks.route('/')
def index():
    return render_template('attacks/index.html', attacks=Attack.query.all())

@attacks.route('/', methods=['POST'])
@login_required
@team_required
def store():
    if current_app.config['RATE_LIMIT_QUANTITY'] > 0:
        rate_limit_quantity = current_app.config['RATE_LIMIT_QUANTITY']
        rate_limit_period = current_app.config['RATE_LIMIT_SECONDS']
        rate_limit_period_ago = datetime.datetime.now() - datetime.timedelta(seconds=rate_limit_period)
        last_minute_attacks = Attack.query.filter(and_(Attack.team_id == current_user.team.id, Attack.created_at > rate_limit_period_ago)).count()
        if last_minute_attacks >= rate_limit_quantity: # They've already submitted the maximum number of attacks
            flash(f"You have been rate limited. You can submit no more than {rate_limit_quantity} attacks per {rate_limit_period} seconds.", category="error")
            return redirect(request.referrer)
        if last_minute_attacks >= (rate_limit_quantity - 1): # This is the last attack they can currently submit
            flash(f"You may be rate limited. You can submit no more than {rate_limit_quantity} attacks per {rate_limit_period} seconds.", category="warning")
    if request.form.get('name') == "":
        flash("No attack name submitted", category="error")
        return redirect(request.referrer)

    # If no attack tarball uploaded, then we're creating an attack by the form.
    if 'attack' in request.files:
        attack = request.files['attack']
        # if user does not select file, browser also
        # submit an empty part without filename
        if not attack or attack.filename == '':
            flash('No file uploaded', category="error")
            return redirect(request.referrer)
    
        try:
            created_attack = create_attack_from_tar(request.form.get('name'), current_user.team_id, attack)
            for team in Team.query.all():
                add_task(team.id, created_attack.id)
            flash(
                f"You've submitted an attack. <a href=\"{ url_for('attacks.show', attack_id=created_attack.id) }\">View/Download it here</a>.",
                category="success"
            )
        except Exception as e:
            flash(str(e), category="error")
    else:
        try:
            created_attack = create_attack_from_post(request.form.get('name'), current_user.team_id, request)
            for team in Team.query.all():
                add_task(team.id, created_attack.id)
            flash(
                f"You've submitted an attack. <a href=\"{ url_for('attacks.show', attack_id=created_attack.id) }\">View/Download it here</a>.",
                category="success"
            )
        except Exception as e:
            flash(str(e), category="error")

    return redirect(request.referrer)

@attacks.route('/<int:attack_id>')
def show(attack_id):
    attack=Attack.query.get_or_404(attack_id)
    return render_template('attacks/show.html', attack=attack)

@attacks.route('/<int:attack_id>/download')
def download(attack_id):
    return send_from_directory('/cctf/attacks', f'{attack_id}.tar.gz', as_attachment=True)

@attacks.route('/create')
@login_required
@team_required
def create():
    return render_template('attacks/create.html')
