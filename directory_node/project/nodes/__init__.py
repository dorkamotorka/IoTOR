import random
import logging
import roundrobin

from marshmallow import ValidationError
from flask import Blueprint, request, jsonify

from project import db
from project.models import Node, NodeSchema
from project.rest import respond

from project.nodes import scheduled

nodes_blueprint = Blueprint('nodes', __name__)
nodes_scheduled = scheduled

node_schema = NodeSchema()
gen = None # Global generator object
new_node = False

def get_node(nodes):
    random.shuffle(nodes)
    rr_list = roundrobin.basic(nodes)
    while True:
        yield rr_list()

@nodes_blueprint.errorhandler(ValidationError)
def handle_error(err):
    """Shows error to the user in a user-friendly way."""
    logging.info(f"Error: {err}")
    return respond(
        success=False,
        message='; '.join([f"{' and '.join([m.removesuffix('.') for m in message])}: '{key}'" for key, message in err.messages.items()]),
        code=500
    )

@nodes_blueprint.route('/node/health', methods=["GET"])
def health():
    """Get health status."""
    return jsonify(dict(status="OK")), 200

@nodes_blueprint.route('/node', methods=["GET"])
def node():
    """List random nodes from the database."""
    global gen, new_node

    max_nodes = int(request.args.get("num_nodes", 3))
    nodes = Node.query.all()
    if max_nodes == -1:
        max_nodes = len(nodes)
    if not len(nodes) >= max_nodes:
        return respond(
            success=False,
            message=f'Currently only {len(nodes)} nodes registered, while minimum of {max_nodes} are required for routing',
            code=500
        )

    # Reset generator object everytime a new node authenticates
    # On instantiation also the list of nodes is shuffled such that 
    # sequence doesn't start always with the same nodes
    if new_node:
        gen = get_node(nodes)
        new_node = False

    result = set()
    for _ in range(max_nodes):
        result.add(next(gen))

    result = list(result)
    random.shuffle(result)
    return respond(
        success=True,
        message="returned {} random nodes".format(len(result)),
        data=[node_schema.dump(node) for node in result]
    )

@nodes_blueprint.route('/admin/node', methods=["POST"])
def add_node():
    """Add a new node to the database."""
    global new_node

    logging.info(f"json: {request.json}")

    node = node_schema.load(request.json)
    addr = node.get_addr() 

    nodes = Node.query.all()
    for n in nodes:
        a = n.get_addr()
        if a == addr:
            db.session.delete(n)
            db.session.commit()

    logging.info(f"insert node: {node}")
    db.session.add(node)
    db.session.commit()
    new_node = True

    return respond(
        success=True,
        message="inserted node",
        data=node_schema.dump(node)
    )
