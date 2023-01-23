import tempfile
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_apscheduler import APScheduler

db = SQLAlchemy()
ma = Marshmallow()
scheduler = APScheduler()

def create_app(test=False) -> Flask:
    """Create a flask app with persistent SQlite backend.

    Parameters:
        test: enable test mode (non-persistent SQlite database)
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(levelname)8s  %(message)s',
    )

    app = Flask(__name__)

    if not test:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    else:
        tmp = tempfile.mkstemp()[1]
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp}.db"

    # register blueprints
    from project.nodes import nodes_blueprint
    app.register_blueprint(nodes_blueprint)

    from project.health import health_blueprint
    app.register_blueprint(health_blueprint)

    # import scheduled tasks
    from project.nodes import nodes_scheduled

    # initialize app (creates databases, tables etc.)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    ma.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    return app
