from flask import Blueprint, render_template, flash, redirect, request
from flask_security import roles_required
from flask_security.utils import hash_password
from web.models.security import User
from web.models.team import Team
from web import db, user_datastore
import os
import shutil
import dulwich.porcelain as git
from dulwich.repo import Repo


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

    # Create git repository for team, and add initial files
    repo_dir = os.path.join('/cctf/repos', str(team.id))
    shutil.copytree('/pack/src', repo_dir)
    os.chdir(repo_dir)
    repo = Repo.init(repo_dir) # Note not init_bare, as we need to add the files. 
    git.add(repo=repo) # Without files specified, defaults to all
    git.commit(repo=repo, message="Initial Commit")

    # Allow pushes to repository.
    # This would normally be done with Dulwich but isn't yet implemented in their library
    # (Currently https://github.com/dulwich/dulwich/blob/debcedf952629e77cd66d1fa0cce1e5079abaa97/dulwich/config.py#L156)
    # using init_bare would solve this problem, if we could use it (see above)
    with open(os.path.join('/cctf/repos/', str(team.id), '.git/config'), "a") as config:
        config.write("[receive]\n\tdenyCurrentBranch = ignore\n")

    flash('Team added successfully', category="success")
    return redirect(request.referrer)

@admin.route('/challenge')
@roles_required('admin')
def challenge():
    return render_template('admin/challenge.html')
