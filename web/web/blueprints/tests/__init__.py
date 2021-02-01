from flask import render_template, Blueprint, make_response, request, abort, flash, redirect, Response, current_app, url_for
from flask_security import login_required, current_user
from web import db, redis, team_required, formatters
from web.models.result import Result
from web.models.team import Team
from web.models.attack import Attack, create_attack_from_post
from web.models.task import add_task
import datetime

tests = Blueprint('tests', __name__, template_folder='templates')

@tests.route('/')
@login_required
@team_required
def index(): # TODO
    return render_template('tests/index.html',
            results=current_user.team.tests_against_gold
    )

@tests.route('/new')
@login_required
@team_required
def create():
    return render_template('tests/create.html',
            passing_results=current_user.team.passing,
            failing_results=current_user.team.failing,
            formatters=formatters,
    )

@tests.route('/<int:result_id>')
@login_required
@team_required
def show(result_id):
    result=Result.query.get_or_404(result_id)
    if result.attack.team_id != current_user.team_id:
        return "Unauthorized", 403
    return render_template('tests/show.html', result=result, formatters=formatters)

@tests.route('/', methods=['POST'])
@login_required
@team_required
def store():
    if current_app.config['RATE_LIMIT_QUANTITY'] > 0:
        rate_limit_quantity = current_app.config['RATE_LIMIT_QUANTITY']
        rate_limit_period = current_app.config['RATE_LIMIT_SECONDS']
        rate_limit_period_ago = datetime.datetime.now() - datetime.timedelta(seconds=rate_limit_period)
        last_minute_attacks = Attack.query.filter(Attack.team_id == current_user.team.id, Attack.created_at > rate_limit_period_ago, Attack.type == "attack").count()
        if last_minute_attacks >= rate_limit_quantity: # They've already submitted the maximum number of attacks
            flash(f"You have been rate limited. You can submit no more than {rate_limit_quantity} tests per {rate_limit_period} seconds.", category="error")
            return redirect(request.referrer)
        if last_minute_attacks >= (rate_limit_quantity - 1): # This is the last attack they can currently submit
            flash(f"You may be rate limited. You can submit no more than {rate_limit_quantity} tests per {rate_limit_period} seconds.", category="warning")
    if request.form.get('name').strip() == "":
        flash("No attack name submitted", category="error")
        return redirect(request.referrer)

    try:
        created_attack = create_attack_from_post(request.form.get('name').strip(), current_user.team_id, request, type="test")
        result = Result()
        result.notes = request.form.get('notes')
        result.submitted_by=current_user
        result.attack = created_attack
        result.seconds_to_complete = 0 # When this becomes nonzero, this is our flag that the result is finished scoring.
        db.session.add(result)
        db.session.commit()
        add_task(current_user.team_id, created_attack.id, 1, {"existing_result": result.id, "force_fail": True}) # high priority places tests ahead of normal scoring on the queue
        flash("Your test is being scored.", category="success")
        return redirect(url_for('tests.show', result_id=result.id))
    except Exception as e:
        flash(str(e), category="error")
        return redirect(request.referrer)
