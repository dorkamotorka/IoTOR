from flask import Blueprint
from flask_restful import Api

chain_api_blueprint = Blueprint('chain_api_blueprint', __name__)
chain_api = Api(chain_api_blueprint)

from . import routes
