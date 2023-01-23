#!/usr/bin/env python3

from cryptography.fernet import Fernet
import base64
import re
import json
import hashlib
import hmac

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import project.onion.util as onion
import rsa


# tests

RSA_KEY_SIZE = 512

def test_build_submsg():
    session_key = Fernet.generate_key()
    public_key, private_key = rsa.newkeys(RSA_KEY_SIZE)
    submsg = json.loads(onion.build_submsg("addr", "payload", session_key, public_key))

    # test structure
    assert "enc_key" in submsg
    assert "enc_payload" in submsg
    assert "hmac" in submsg

    # test crypto

    # asymmetric
    assert rsa.decrypt(base64.b64decode(submsg["enc_key"]), private_key) == session_key

    # symmetric
    assert json.loads(Fernet(session_key).decrypt(base64.b64decode(submsg["enc_payload"])).decode()) == {"dst": "addr", "enc_payload": "payload"}

    # integrity
    to_authenticate = dict(
        enc_key=submsg["enc_key"],
        enc_payload=submsg["enc_payload"]
    )
    assert hmac.compare_digest(
        submsg["hmac"],
        hmac.new(session_key, json.dumps(to_authenticate).encode(), hashlib.sha256).hexdigest()
    )


def test_build_msg():
    chain = [
        "127.0.0.1:1",
        "127.0.0.1:2",
        "127.0.0.1:3",
        "end",
    ]
    public_keys = [rsa.newkeys(RSA_KEY_SIZE)[0] for _ in range(3)]
    sym_keys = [Fernet.generate_key() for _ in range(3)]
    payload = "test"
    endpoint = "testendpoint"
    output = onion.build_msg(chain, public_keys, sym_keys, payload, endpoint, [])

    # test structure: key should be base64, payload should be base64, hmac should be hexdigest
    assert "enc_key" in output
    assert len(base64.b64decode(output["enc_key"])) == RSA_KEY_SIZE / 8

    assert "enc_payload" in output
    assert len(base64.b64decode(output["enc_payload"])) >= 1000

    assert "hmac" in output
    assert re.match(r"[a-f0-9]{64}", output["hmac"])
