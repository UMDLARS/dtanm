from flask import render_template, Blueprint, flash, request, url_for, redirect, send_from_directory
from flask_security import login_required, current_user
from web.models.attack import Attack, create_attack
from werkzeug.utils import secure_filename
from web.models.task import add_task
from web import db
import os

attacks = Blueprint('attacks', __name__, template_folder='templates')

@attacks.route('/')
def index():
    return render_template('attacks/index.html', attacks=Attack.query.all())

@attacks.route('/', methods=['POST'])
@login_required
def store():
    rate_limited = False
    if rate_limited:
        flash("You may be rate limited. You can submit no more than six attacks per minute.", category="warning")
        flash("You may be rate limited. You can submit no more than six attacks per minute.", category="error")
        return redirect(request.referrer)

    # check if the post request has the file part
    if 'attack' not in request.files:
        flash('No file attribute in request', category="error")
        return redirect(request.referrer)

    attack = request.files['attack']
    # if user does not select file, browser also
    # submit an empty part without filename
    if not attack or attack.filename == '':
        flash('No file uploaded', category="error")
        return redirect(request.referrer)

    try:
        created_attack = create_attack('attack_name_here', current_user.team_id, attack)
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
def create():
    return render_template('attacks/create.html')