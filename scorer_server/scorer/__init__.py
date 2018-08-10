import logging
import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        START_TASKER=False,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    app.logger.info('Logging setup')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from scorer import api
    app.register_blueprint(api.bp)

    if app.config['START_TASKER']:
        # This is a hack to make only one Tasker object when debugging.
        if not app.config['DEBUG'] or (app.config['DEBUG'] and os.environ.get("WERKZEUG_RUN_MAIN") == "true"):
            from scorer import tasker

            @app.before_first_request
            def start_tasker():
                tasker.init_app()

    return app
