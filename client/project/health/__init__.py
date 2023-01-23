from flask import Blueprint, jsonify

blueprint = Blueprint('health', __name__)

@blueprint.route('/health', methods=["GET"])
def health():
    """
    Get health status.
    """
    return jsonify(dict(status="OK")), 200
