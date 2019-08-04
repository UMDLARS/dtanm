from flask import Blueprint, render_template
from flask_security import roles_required

admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route('/')
@roles_required('admin')
def index():
    return render_template('admin/index.html')