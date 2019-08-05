import logging
import os

from flask import Flask, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from redis import Redis

db = SQLAlchemy()

redis = None
user_datastore = None

def create_app():
    global user_datastore, redis
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')

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
    db.init_app(app)

    redis=Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                 port=os.environ.get('REDIS_PORT', 6379),
                 db=os.environ.get('REDIS_DB', 0))

    # Setup Flask-Security
    from web.models.security import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Create a user to test with
    @app.before_first_request
    def create_user():
        db.create_all()
        user_datastore.find_or_create_role(name='admin', description='Administrator')

        admin_email = os.environ.get('ADMIN_USER_EMAIL')
        admin_password  = os.environ.get('ADMIN_USER_PASSWORD')

        if not user_datastore.get_user(admin_email):
            user_datastore.create_user(email=admin_email, password=admin_password)
        db.session.commit()

        user_datastore.add_role_to_user(admin_email, 'admin')
        db.session.commit()

    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)

    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    app.logger.info('Logging setup')

    # The following is equivalent to this for each blueprint:
    # from blueprints import instructions
    # app.register_blueprint(instructions.instructions, url_prefix='/instructions')
    for blueprint_name in ["admin", "attacks", "instructions", "teams"]:
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


    from web.models.result import Result

    @app.route('/results.json')
    def results():
        return Result.query.all()

    return app
