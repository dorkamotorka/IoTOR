from flask import Blueprint, request, render_template, send_from_directory
from project.onion import util
import os

blueprint = Blueprint('onion', __name__)
DIR_NODE_URL = os.environ.get("DIRECTORY_NODE_URL", "http://localhost:5000")

@blueprint.route('/', methods=["GET", "POST"])
def main():
    """
    return onion service UI for the weather endpoint
    """
    if request.method == "GET":
        # GET: render empty site with just a button
        return render_template("index.html")
    else:
        # POST: requests weather via onion service
        response = util.request(DIR_NODE_URL, "get_weather", "weather", 'weather_api:4000')
        return render_template("index.html", response=response)

@blueprint.route('/assets/<path:path>', methods=["GET"])
def assets(path: str):
    """
    return static assets, e.g. images

    :param path: relative path to static asset
    """
    return send_from_directory('assets', path)
