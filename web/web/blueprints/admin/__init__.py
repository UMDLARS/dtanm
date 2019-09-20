from flask import Blueprint, render_template, flash, redirect, request, url_for
from flask_security import roles_required
from flask_security.utils import hash_password
from web.models.security import User
from web.models.team import Team
from web import db, user_datastore

import os
import tempfile
import csv

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
    user = User()
    user.email = request.form['email']
    user.password = hash_password('password')
    user.name = request.form['name']
    user_datastore.activate_user(user)
    db.session.add(user)
    db.session.commit()
    flash('User added successfully with generated password <code>password</code>', category="success")
    return redirect(request.referrer)

@admin.route('/set_user_team', methods=['POST'])
@roles_required('admin')
def set_user_team():
    user = User.query.get(int(request.form['userid']))
    user.team = Team.query.get(int(request.form['teamid']))
    db.session.commit()
    flash('User team set successfully', category="success")
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

    flash('Team added successfully', category="success")
    return redirect(request.referrer)

@admin.route('/challenge')
@roles_required('admin')
def challenge():
    return render_template('admin/challenge.html')

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

    import_data_file = tempfile.mktemp()
    import_data.save(import_data_file)
    with open(import_data_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None)
        name_col = headers.index('Name')
        email_col = headers.index('Email')
        team_col = headers.index('Team')
        try: # Passwords are optional
            password_col = headers.index('Password')
        except ValueError: # Column not found
            password_col = None
        for row in reader:
            team = Team.query.filter(Team.name == row[team_col]).first()
            if team is None:
                team = Team()
                team.name = row[team_col]
                db.session.add(team)
                db.session.commit()
                team.set_up_repo()

            user = User()
            user.name = row[name_col]
            user.email = row[email_col]
            user.password = hash_password('password' if password_col is None else row[password_col])
            user.team = team
            user_datastore.activate_user(user)
            db.session.add(user)
            db.session.commit()

    os.remove(import_data_file)
    flash('User import completed successfully', category="success")
    return redirect(url_for('admin.users'))
