from flask import render_template, Blueprint, flash, request, url_for, redirect
from flask_security import login_required, current_user
from web.models.attack import Attack
from werkzeug.utils import secure_filename
from web.models.task import add_task
from web import db

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
        return redirect(request.url)

    attack = request.files['attack']
    # if user does not select file, browser also
    # submit an empty part without filename
    if not attack or attack.filename == '':
        flash('No file uploaded', category="error")
        return redirect(request.url)

    filename = secure_filename(attack.filename)
    attack.save(os.path.join(app.config['UPLOAD_DIR'], filename))
    app.logger.debug(f"New Attack submitted: '{filename}'")
    attack = get_attack_manager().process_attack(filename)

    add_attack(attack.id)

    attack = Attack()
    db.session.add(attack)
    db.session.commit()

    flash(f"You've submitted an attack. <a href=\"{ url_for('attacks.show', attack_id=attack.id) }\">View/Download it here</a>.", category="success")
    return redirect(request.referrer)

@attacks.route('/<int:attack_id>')
def show(attack_id):
    attack=Attack.query.get_or_404(attack_id)
    return render_template('attacks/show.html', attack=attack)

@attacks.route('/create')
@login_required
def create():
    return render_template('attacks/create.html')