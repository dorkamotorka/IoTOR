import logging
import requests
from project import db, scheduler
from project.models import Node

@scheduler.task("interval", id="clean_nodes", seconds=60, coalesce=True, max_instances=1)
def clean_nodes(timeout=5):
    """
    Non-reachable chain nodes (error on /health) get evicted from the node directory every minute.
    """
    with scheduler.app.app_context():
        for node in Node.query.all():
            logging.info(f"Health checking {node.address}...")
            try:
                response = requests.get(f"http://{node.address}/health", timeout=timeout)
                response.raise_for_status()
                logging.info(f"OK: {node.address}")
            except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.Timeout) as e:
                logging.warning(f"Removing node={node.address} because of exception={e}")
                db.session.delete(node)
                db.session.commit()
