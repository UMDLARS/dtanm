import logging
import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin

"""Create and configure an instance of the Flask application."""
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    # a default secret that should be overridden by instance config
    SECRET_KEY='dev',
    START_TASKER=False,
)

# MongoDB Config for Flask-Security
app.config['MONGODB_DB'] = os.environ.get('MONGO_DB', 'scorer')
app.config['MONGODB_HOST'] = os.environ.get('MONGO_HOST', 'localhost')
app.config['MONGODB_PORT'] = os.environ.get('MONGO_PORT', 27017)

app.config['SECURITY_REGISTERABLE'] = True
# app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = '6cPE1/Pn+rfq+HvdmdCpucAP3kcJyz+k' # TODO: dynamic config
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

# Create database connection object
db = MongoEngine(app)

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    user_datastore.create_user(email='swift106@d.umn.edu', password='password')

# load the instance config, if it exists, when not testing
app.config.from_pyfile('config.py', silent=True)

if app.debug:
    app.logger.setLevel(logging.DEBUG)

app.logger.info('Logging setup')

from scorer import ui
app.register_blueprint(ui.ui_bp)
from scorer import api
app.register_blueprint(api.bp, url_prefix='/api')

if __name__ == '__main__':
    app.run()
