from flask import Blueprint, render_template, flash, redirect, request, url_for
from flask_security import roles_required, current_user, url_for_security
from flask_security.recoverable import generate_reset_password_token
from flask_security.utils import hash_password
from web.models.security import User
from web.models.team import Team, Badge
from web.models.task import add_task
from web.models.attack import Attack
from web import db, user_datastore

import shutil
import os
import io
import csv
import secrets
import string

admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route('/')
@roles_required('admin')
def index():
    return render_template('admin/index.html')

@admin.route('/users')
@roles_required('admin')
def users():
    return render_template('admin/users.html', users=User.query.all(), teams=Team.query.all())

@admin.route('/add_user', methods=['POST'])
@roles_required('admin')
def add_user():
    if request.form['email'].strip() == "":
        flash("User email cannot be empty.", category="error")
        return redirect(request.referrer)

    user = User()
    user.email = request.form['email']
    user.name = request.form['name']

    if request.form["teamid"] != "":
        team_id = int(request.form["teamid"])
        user.team = Team.query.get(team_id)

    if request.form['password'] == "":
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    else:
        password = request.form['password']
    user.password = hash_password(password)

    user_datastore.activate_user(user)
    db.session.add(user)
    db.session.commit()
    flash(f'User added with password <code>{password}</code>', category="success")
    return redirect(request.referrer)

@admin.route('/update_user', methods=['POST'])
@roles_required('admin')
def update_user():
    user = User.query.get(int(request.form['userid']))
    if request.form['teamid']:
        user.team = Team.query.get(int(request.form['teamid']))
    else:
        user.team = None
    user.name = request.form['name']
    user.email = request.form['email']
    if request.form.get('administrator'):
        user_datastore.add_role_to_user(user, 'admin')
    else:
        if user == current_user:
            flash('You may not remove your own administrative privileges', category="error")
        else:
            user_datastore.remove_role_from_user(user, 'admin')
    db.session.commit()
    flash(f'User {user.email} updated', category="success")
    return redirect(request.referrer)

@admin.route('/update_team', methods=['POST'])
@roles_required('admin')
def update_team():
    team = Team.query.get(int(request.form['teamid']))
    team.name = request.form['name']
    db.session.commit()
    flash(f'Team {team.name} updated', category="success")
    return redirect(request.referrer)

@admin.route('/teams')
@roles_required('admin')
def teams():
    return render_template('admin/teams.html', teams=Team.query.all())

@admin.route('/add_team', methods=['POST'])
@roles_required('admin')
def add_team():
    team = Team()
    team.name = request.form['name']
    db.session.add(team)
    db.session.commit()
    team.set_up_repo()
    team.rescore_all_attacks()

    flash('Team added', category="success")
    return redirect(request.referrer)

@admin.route('/teams/<int:team_id>/delete', methods=['POST'])
@roles_required('admin')
def delete_team(team_id: int):
    team = Team.query.get(team_id)
    for member in team.members:
        member.team = None
    db.session.delete(team)
    db.session.commit()
    shutil.rmtree(os.path.join('/cctf/repos', str(team_id)))

    flash('Team deleted', category="success")
    return redirect(request.referrer)

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@roles_required('admin')
def delete_user(user_id: int):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    flash('User deleted', category="success")
    return redirect(request.referrer)

@admin.route('/challenge')
@roles_required('admin')
def challenge():
    return render_template('admin/challenge.html')

@admin.route('/rescore_all')
@roles_required('admin')
def rescore_all():
    for team in Team.query.all():
        for attack in Attack.query.all():
            add_task(team.id, attack.id)
    flash('All attacks have been added to the rescore queue.', category="success")
    return redirect(request.referrer)

@admin.route('/teams/<int:team_id>/rescore')
@roles_required('admin')
def rescore_team(team_id: int):
    for attack in Attack.query.all():
        add_task(team_id, attack.id)
    flash(f'All attacks for Team {Team.query.get(team_id).name} have been added to the rescore queue.', category="success")
    return redirect(request.referrer)

@admin.route('/import_users')
@roles_required('admin')
def show_user_import():
    return render_template('admin/import_users.html')

@admin.route('/import_users', methods=['POST'])
@roles_required('admin')
def import_users():
    import_data = request.files['import_data']
    # if user does not select file, browser also
    # submit an empty part without filename
    if not import_data or import_data.filename == '':
        flash('No file uploaded', category="error")
        return redirect(request.referrer)

    reader = csv.DictReader(io.TextIOWrapper(import_data))
    for row in reader:
        team = Team.query.filter(Team.name == row['Team']).first()
        if team is None:
            team = Team()
            team.name = row['Team']
            db.session.add(team)
            db.session.commit()
            team.set_up_repo()
            team.rescore_all_attacks()

        user = User()
        user.name = row['Name']
        user.email = row['Email']
        user.password = hash_password(row['Password'] if 'Password' in row else 'password')
        user.team = team
        user_datastore.activate_user(user)
        db.session.add(user)
        db.session.commit()

    flash('User import completed', category="success")
    return redirect(url_for('admin.users'))

@admin.route('/users/<int:user_id>/reset_password_link')
@roles_required('admin')
def reset_user_password(user_id: int):
    user = User.query.get(user_id)

    token = generate_reset_password_token(user)
    reset_link = url_for_security(
        'reset_password', token=token, _external=True
    )

    return reset_link

@admin.route('/badges', methods=['POST'])
@roles_required('admin')
def create_badge():
    badge = Badge()
    badge.team_id = request.form['team_id']
    badge.type = request.form['type']
    badge.content = request.form['content']
    db.session.add(badge)
    db.session.commit()

    flash('Badge added', category="success")
    return redirect(request.referrer)

@admin.route('/badges/<int:badge_id>/delete', methods=['POST'])
@roles_required('admin')
def delete_badge(badge_id: int):
    badge = Badge.query.get(badge_id)
    db.session.delete(badge)
    db.session.commit()
    return "ok"
