import logging
from flask import Flask

def create_app() -> Flask:
    """
    Create a flask app
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(levelname)8s  %(message)s',
    )

    app = Flask(__name__)

    # register blueprints
    import project.onion
    app.register_blueprint(project.onion.blueprint)

    import project.health
    app.register_blueprint(project.health.blueprint)

    return app
