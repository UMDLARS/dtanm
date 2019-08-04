from flask import Blueprint, render_template, flash, redirect, request
from flask_security import roles_required
from flask_security.utils import hash_password
from web.models.security import User
from web.models.team import Team
from web import db, user_datastore

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
    flash('Team added successfully', category="success")
    return redirect(request.referrer)

@admin.route('/challenge')
@roles_required('admin')
def challenge():
    return render_template('admin/challenge.html')
