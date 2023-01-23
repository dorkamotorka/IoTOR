from flask import Blueprint, jsonify

from project import db

health_blueprint = Blueprint('health', __name__)

@health_blueprint.route('/health', methods=["GET"])
def health():
    """Get health status."""

    if db.session.execute("SELECT 1").returns_rows:
        return jsonify(dict(status="OK")), 200
    else:
        return jsonify(dict(status="DB UNHEALTHY")), 500
