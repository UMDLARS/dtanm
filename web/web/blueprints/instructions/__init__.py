from flask import Blueprint, render_template, abort, url_for
from jinja2 import Template
from werkzeug.utils import secure_filename
import os

instructions = Blueprint('instructions', __name__, template_folder='templates')

def format_doc(file):
    return Template(file.read()).render(
        DTANM_LINK_INSTRUCTIONS = url_for('instructions.show'),
        DTANM_LINK_PROGRAM      = url_for('program.index'),
        DTANM_LINK_MY_SCORE     = url_for('teams.me'),
        DTANM_LINK_TEAMS        = url_for('teams.index'),
        DTANM_LINK_ATTACKS      = url_for('attacks.index'),
        DTANM_LINK_STATS        = url_for('stats'),
        DTANM_LINK_ADMIN        = url_for('admin.index')
    )


@instructions.route('/', defaults={'page': 'index'})
@instructions.route('/<page>')
def show(page):
    base_file=f'/pack/docs/{secure_filename(page)}'
    if os.path.isfile(base_file+'.html'):
        with open(base_file+'.html') as file:
            return render_template('instructions/index.html', page=format_doc(file), format="html")
    elif os.path.isfile(base_file+'.md'):
        with open(base_file+'.md') as file:
            return render_template('instructions/index.html', page=format_doc(file), format="markdown")
    elif os.path.isfile(base_file+'.txt'):
        with open(base_file+'.txt') as file:
            return render_template('instructions/index.html', page=format_doc(file), format="text")
    else:
        abort(404)
