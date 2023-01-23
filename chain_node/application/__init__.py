import rsa
import requests
from flask import Flask
import logging

def create_app():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(levelname)8s  %(message)s',
    )

    """Create Flask application."""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Announce availability to directory node
    public_key, private_key = rsa.newkeys(3072)
    app.config["PRIVATE_KEY"] = private_key
    pk_pem = public_key.save_pkcs1('PEM')
    resp = requests.post(app.config["DIR_NODE_URL"] + "/admin/node", json={"name": f"{app.config['NAME']}",
                                                         "kind": f"{app.config['TYPE']}",
                                                         "address": f"{app.config['HOST']}:{app.config['PORT']}",
                                                         "public_key": pk_pem.decode()})
    if not resp.status_code == 200:
        logging.error(f"Failed to authenticate {app.config['TYPE']} node to directory node!")
        exit(1)

    logging.info(f"==== Running {app.config['TYPE']} node on {app.config['HOST']}:{app.config['PORT']}...")


    with app.app_context():
        # Import blueprints 
        from .api import chain_api_blueprint

        # Register Blueprints
        app.register_blueprint(chain_api_blueprint)

        return app 
