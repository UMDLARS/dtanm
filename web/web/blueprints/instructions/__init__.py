from flask import Blueprint, render_template, abort
from werkzeug.utils import secure_filename
import os

instructions = Blueprint('instructions', __name__, template_folder='templates')

@instructions.route('/', defaults={'page': 'index'})
@instructions.route('/<page>')
def show(page):
    base_file=f'pack/instructions/{secure_filename(page)}'
    if os.path.isfile(base_file+'.html'):
        with open(base_file+'.html') as file:
            return render_template('instructions.html', page=file.read(), format="html")
    elif os.path.isfile(base_file+'.md'):
        with open(base_file+'.md') as file:
            return render_template('instructions.html', page=file.read(), format="markdown")
    elif os.path.isfile(base_file+'.txt'):
        with open(base_file+'.txt') as file:
            return render_template('instructions.html', page=file.read(), format="text")
    else:
        abort(404)