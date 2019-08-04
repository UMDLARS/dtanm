import logging
import os

from flask import Flask, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = 'dev'

    # Database Config for Flask-Security
    app.config['POSTGRES_HOST'] = os.environ.get('POSTGRES_HOST', 'postgres')
    app.config['POSTGRES_DB'] = os.environ.get('POSTGRES_DB', 'postgres')
    app.config['POSTGRES_USER'] = os.environ.get('POSTGRES_USER', 'postgres')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{app.config["POSTGRES_USER"]}@{app.config["POSTGRES_HOST"]}/{app.config["POSTGRES_DB"]}'

    # Other Config for Flask-Security
    app.config['SECURITY_REGISTERABLE'] = True
    # app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_PASSWORD_SALT'] = '6cPE1/Pn+rfq+HvdmdCpucAP3kcJyz+k' # TODO: dynamic config
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

    # Create database connection object
    db = SQLAlchemy(app)

    # Define models
    roles_users = db.Table('roles_users',
            db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
            db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

    class Role(db.Model, RoleMixin):
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(80), unique=True)
        description = db.Column(db.String(255))

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True)
        password = db.Column(db.String(255))
        active = db.Column(db.Boolean())
        confirmed_at = db.Column(db.DateTime())
        roles = db.relationship('Role', secondary=roles_users,
                                backref=db.backref('users', lazy='dynamic'))

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Create a user to test with
    @app.before_first_request
    def create_user():
        db.create_all()
        db.session.commit()

        import sqlalchemy.exc
        try:
            user_datastore.create_user(email='swift106@d.umn.edu', password='password')
            db.session.commit()
        except sqlalchemy.exc.IntegrityError: # If the user already exists
            db.session().rollback()

    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)

    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    app.logger.info('Logging setup')

    # The following is equivalent to this for each blueprint:
    # from blueprints import instructions
    # app.register_blueprint(instructions.instructions, url_prefix='/instructions')
    for blueprint_name in ["instructions"]:
        blueprint = __import__("web.blueprints."+blueprint_name, fromlist=[''])
        app.register_blueprint(getattr(blueprint, blueprint_name), url_prefix='/'+blueprint_name)


    from web.scorer import ui
    app.register_blueprint(ui.ui_bp)
    from web.scorer import api
    app.register_blueprint(api.bp, url_prefix='/api')


    @app.context_processor
    def utility_processor():
        def create_menu_item(title: str, route_name: str):
            """
            Creates HTML for sidebar menu item, and highlights it if active

            Parameters:
                title (str): The displayed text of the menu item
                route_name (str): the Python path to the route (e.g. 'ui.index')
            """
            selected_class = "active" if request.path == url_for(route_name) else "bg-light"
            return f"<a href=\"{ url_for(route_name) }\" class=\"list-group-item list-group-item-action { selected_class }\">{title}</a>" 
        return dict(create_menu_item=create_menu_item)
    return app
