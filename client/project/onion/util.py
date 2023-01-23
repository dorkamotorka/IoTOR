import hashlib
import hmac
import json
import logging
from base64 import b64encode
from time import sleep
from datetime import datetime

import rsa
import requests
from cryptography.fernet import Fernet, InvalidToken


def log(logs: list[dict], level: str, message: dict) -> None:
    """
    logs to python logger and adds log to given {logs} list at the same time
    """

    now = datetime.now()
    message["date"] = now.strftime("%Y-%m-%d")
    message["time"] = now.strftime("%H:%M:%S.%f")
    logs.append(message)
    logging.log(logging.getLevelName(level.upper()), message)


def trunc(data, limit=128) -> str:
    """
    truncates given {data} as a string to a limit {limit}
    """

    if isinstance(data, bytes):
        data = data.decode()
    else:
        data = str(data).strip('"')

    size = len(data)
    if len(data) > limit:
        data = data[0:limit] + "[…]"
    return f"{data} (len={size})"


def request(directory_node_url: str, payload: str, endpoint: str, endpoint_address: str, max_retries=20, timeout=3) -> dict:
    """
    makes a request to the endpoint via the onion routing.

    :param payload: payload to request from the endpoint (e.g. "get_weather")
    :param endpoint: endpoint name (e.g. "weather")
    :param endpoint_address: endpoint address
    :param max_retries: max number of retries after the request is seen as unsuccessful
    :param timeout: timeout after which a single request fails
    """

    tries = 0
    logs = []
    msg = None

    # Resend msg until succesfully received
    while tries < max_retries:
        logging.info(f"Requesting nodes from {directory_node_url}")
        try:
            directory_chain_response = requests.get(directory_node_url + "/node", params={'num_nodes': '3'})
            directory_chain_response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
            log(logs, "error", dict(message=f"Failed to establish communication with directory node. Error: {e}"))
            log(logs, "info", dict(message="Retrying connecting to the directory node..."))
            sleep(1)
            tries += 1
            continue

        nodes = directory_chain_response.json()['data']
        logging.info(f"Retrieved chain node sequence from {directory_node_url}: {[n['name'] for n in nodes]}")

        chain = []
        public_keys = []
        for node in nodes:
            chain.append(node['address'])
            public_keys.append(rsa.PublicKey.load_pkcs1(node['public_key'].encode(), 'PEM'))

        chain.append(endpoint_address) # append server IP

        if len(chain) < 4:
            logging.critical(f"Chain did not have enough elements: {chain}")
            sleep(1)
            tries += 1

        # 3 symmetric keys otherwise entry, intermediary, exit node can decrypt msgs between each other
        sym_keys = [Fernet.generate_key() for _ in range(3)]

        for key in sym_keys:
            logging.info(f"Generated symmetric session key: {trunc(key, 8)}")
        logging.info("")

        logging.info(f"Using payload='{payload}' for endpoint='{endpoint}' at address='{endpoint_address}'")
        msg = build_msg(chain, public_keys, sym_keys, payload, endpoint, logs)

        done, result = run(msg, sym_keys, chain[0], timeout)
        if done:
            return dict(result=result, chain=reversed(nodes), logs=logs)

        tries += 1

    return dict(result=[], chain=[], logs=logs)


def run(msg: dict, sym_keys: list[bytes], entry_node: str, timeout: int) -> tuple[bool, str]:
    """
    builds message for the entry node (with all messages for the intermediate nodes and the exit node) and sends it to the entry node.

    :param msg: message to send to the entry node
    :param sym_keys: list of symmetric/session keys
    :param entry_node: address of entry node
    :param timeout: timeout after which the request fails

    :returns: tuple with information if the request has been successful and the result/output string from the endpoint
    """

    success = False
    result = ""

    try:
        resp = requests.post(f"http://{entry_node}/node/forward", msg, timeout=timeout)
        enc_data = resp.json()
        for key in sym_keys:
            sym_key = Fernet(key)
            logging.info(f"Decrypting with key={trunc(key, 8)}: '{trunc(enc_data)}'")
            enc_data = sym_key.decrypt(enc_data).decode('utf-8')
            enc_data = enc_data.strip('0')
            logging.info(f"Decrypted: '{trunc(enc_data)}'")
            result = json.loads(enc_data)
        success = True
    except (requests.exceptions.JSONDecodeError, requests.Timeout, requests.exceptions.ConnectionError, InvalidToken) as e:
        logging.error(f"Failed to receive a response. Error: {e}")
        logging.info("Resending msg...")

    return (success, result)


def build_submsg(dst: str, payload: str, sk: bytes, pk: rsa.PublicKey, request=False, endpoint=None) -> str:
    """
    builds one intermediate/sub-message destined for one of the nodes.

    :param dst: destination address
    :param payload: payload destined for the node
    :param sk: secret/session key to encrypt the payload with
    :param pk: public key to encrypt the session key with
    :param request: if message is the request to the final endpoint
    :param endpoint: the final endpoint address

    :returns: the submessage as JSON
    """

    if request:
        payload = json.dumps({'dst': dst, 'enc_payload': payload, 'endpoint': endpoint})
    else:
        payload = json.dumps({'dst': dst, 'enc_payload': payload})

    enc_payload = Fernet(sk).encrypt(payload.encode('utf-8'))
    enc_sk = rsa.encrypt(sk, pk)

    # Convert to base64 for sending over the network
    b64_enc_payload = b64encode(enc_payload).decode('utf-8')
    b64_enc_sk = b64encode(enc_sk).decode('utf-8')
    msg = json.dumps({'enc_key': b64_enc_sk, 'enc_payload': b64_enc_payload})
    integrity = hmac.new(sk, msg.encode('utf-8'), hashlib.sha256)
    logging.info(f"Payload HMAC for destination {dst}: '{integrity.hexdigest()}'")

    return json.dumps({'enc_key': b64_enc_sk, 'enc_payload': b64_enc_payload, 'hmac': integrity.hexdigest()})


def build_msg(chain: list[str], public_keys: list[rsa.PublicKey], sym_keys: list[bytes], request_payload: str, endpoint: str, logs: list[dict]) -> dict:
    """
    builds the message to send to the entry node with all the data for the nodes in between

    :param chain: list of chain node addresses
    :param public_keys: list of public keys for the chain
    :param sym_keys: list of generated symmetric/session keys
    :param request_payload: payload to send to the endpoint
    :param endpoint: endpoint address to access
    :param logs: list of log messages to send to the user

    :returns: the message object to send to the entry node
    """

    entry_ip, intermediary_ip, exit_ip, server_ip = chain[0:4]
    entry_pk, intermediary_pk, exit_pk = public_keys
    entry_sk, intermediary_sk, exit_sk = sym_keys

    enc_exit_msg = build_submsg(server_ip, request_payload, exit_sk, exit_pk, request=True, endpoint=endpoint)
    log(logs, "info", dict(
        envelope="exit",
        payload=trunc(request_payload),
        session_key=trunc(exit_sk, 8),
        public_key=trunc(exit_pk, 16),
        result=trunc(enc_exit_msg),
        message=f"Encrypting message '{trunc(request_payload)}' with session key '{trunc(exit_sk,8)}' and session key with public key of exit node '{trunc(exit_pk, 16)}': --> {trunc(enc_exit_msg)}")
    )

    enc_intermediary_msg = build_submsg(exit_ip, enc_exit_msg, intermediary_sk, intermediary_pk)
    log(logs, "info", dict(
        envelope="intermediate",
        payload=trunc(enc_exit_msg),
        session_key=trunc(intermediary_sk, 8),
        public_key=trunc(intermediary_pk, 16),
        result=trunc(enc_intermediary_msg),
        message=f"Encrypting message '{trunc(enc_exit_msg)}' with session key '{trunc(intermediary_sk,8)}' and session key with public key of intermediate node '{trunc(intermediary_pk,16)}': --> {trunc(enc_intermediary_msg)}")
    )

    enc_entry_msg = build_submsg(intermediary_ip, enc_intermediary_msg, entry_sk, entry_pk)
    log(logs, "info", dict(
        envelope="entry",
        payload=trunc(enc_intermediary_msg),
        session_key=trunc(entry_sk, 8),
        public_key=trunc(entry_pk, 16),
        result=trunc(enc_entry_msg),
        message=f"Encrypting message '{trunc(enc_intermediary_msg)}' with session key '{trunc(entry_sk,8)}' and session key with public key of entry node '{trunc(entry_pk, 16)}': --> {trunc(enc_entry_msg)}")
        )

    logging.info("")
    logging.info(f"Message to send to entry node: '{trunc(enc_entry_msg)}'")
    logging.info("")
    return json.loads(enc_entry_msg)
