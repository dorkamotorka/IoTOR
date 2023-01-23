import sys
import rsa
import json
import hmac
import hashlib
import random
from cryptography.fernet import Fernet
from base64 import b64decode
import logging

def trunc(d, limit=128) -> str:
    try:
        d = d.decode()
    except AttributeError:
        d = str(d).strip('"')

    size = len(d)
    if size > limit:
        d = d[0:limit] + "[…]"
    return f"{d} (len={size})"

def get_random_pad_length(limit):
    return random.randint(0, limit)

def unpack_msg(enc_data, private_key):
    enc_key = b64decode(enc_data['enc_key'])
    msg_length = len(enc_data['enc_payload'])
    enc_data['enc_payload'] = enc_data['enc_payload'].strip('0')
    enc_payload = b64decode(enc_data['enc_payload'])
    received_hmac = enc_data['hmac']

    try:
        wrapped_key = rsa.decrypt(enc_key, private_key)
    except rsa.pkcs1.DecryptionError as e:
        logging.error(f"Error while decrypting: {e}")
        return None, None, None, None
    msg = json.dumps({'enc_key': enc_data['enc_key'], 'enc_payload': enc_data['enc_payload']})
    msg_hmac = hmac.new(wrapped_key, msg.encode('utf-8'), hashlib.sha256)
    if not hmac.compare_digest(received_hmac, msg_hmac.hexdigest()):
        logging.error("HMAC doesn't match - msg was tampered!")
        return None, None, None, None

    logging.info(f"Using session key {trunc(wrapped_key,8)}")
    sym_key = Fernet(wrapped_key)
    data = sym_key.decrypt(enc_payload).decode('utf-8')

    data = json.loads(data)
    logging.info(f"DECRYPTED DATA: {trunc(data)}")
    next_hop = data["dst"]
    endpoint = None
    if 'endpoint' in data:
        endpoint = data["endpoint"]
        enc_payload = data["enc_payload"]
    else:
        enc_payload = json.loads(data["enc_payload"])

        # Randomize length of padding to prevent msg correlation
        pad_length = get_random_pad_length(msg_length)
        enc_payload["enc_payload"] = enc_payload["enc_payload"].zfill(pad_length)
    return sym_key, next_hop, enc_payload, endpoint
