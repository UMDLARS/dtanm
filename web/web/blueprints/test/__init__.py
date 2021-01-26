from os import F_TEST
from flask import render_template, Blueprint, make_response, request, abort, flash, redirect, Response
from flask_security import login_required, current_user
from web import db, redis, team_required

test = Blueprint('test', __name__, template_folder='templates')

@test.route('/')
@login_required
@team_required
def index():
    return render_template('test/index.html')


