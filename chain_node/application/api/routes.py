import json
import requests
from flask_restx import Resource, reqparse
from flask import jsonify, make_response, current_app, request
from . import chain_api, util
import logging

class Health(Resource):
    def get(self):
        return make_response(jsonify(dict(status="OK")), 200)

class ChainNode(Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("enc_key", type=str, required=True)
        self.parser.add_argument("enc_payload", type=str, required=True)
        self.parser.add_argument("hmac", type=str, required=True)

        super(ChainNode, self).__init__(*args, **kwargs)

    def post(self):
        """
        Forward request
        """
        args = self.parser.parse_args()
        logging.info(f"Received POST from {request.remote_addr}: payload={util.trunc(args)}")

        sym_key, next_hop, payload, endpoint = util.unpack_msg(args, current_app.config["PRIVATE_KEY"])
        if endpoint is None:
            logging.info(f"Forwarding to next_hop={next_hop} payload={util.trunc(payload)}")
            resp = requests.post(f"http://{next_hop}/node/forward", payload)
        else:
            logging.info(f"Talking to final endpoint={endpoint} at next_hop={next_hop} with payload={util.trunc(payload)}")
            resp = requests.get(f"http://{next_hop}/{endpoint}")
        data = json.dumps(resp.json())

        # Randomize length of padding to prevent msg correlation
        limit = len(json.dumps(payload))
        pad_length = util.get_random_pad_length(limit)
        data = data.zfill(pad_length)
        logging.info(f"Encrypting with session key: '{util.trunc(data)}'")
        enc_data = sym_key.encrypt(data.encode('utf-8'))

        logging.info(f"Responding to {request.remote_addr} with payload={util.trunc(enc_data)}")
        return make_response(jsonify(enc_data.decode('utf-8')), 200)

chain_api.add_resource(ChainNode, "/node/forward")
chain_api.add_resource(Health, "/health")
