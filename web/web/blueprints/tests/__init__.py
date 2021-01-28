from flask import render_template, Blueprint, make_response, request, abort, flash, redirect, Response
from flask_security import login_required, current_user
from web import db, redis, team_required, formatters

tests = Blueprint('tests', __name__, template_folder='templates')

@tests.route('/')
@login_required
@team_required
def index(): # TODO
    return render_template('tests/index.html',
            passing_results=current_user.team.passing,
            failing_results=current_user.team.failing,
            formatters=formatters,
    )

@tests.route('/new')
@login_required
@team_required
def create():
    return render_template('tests/index.html',
            passing_results=current_user.team.passing,
            failing_results=current_user.team.failing,
            formatters=formatters,
    )
