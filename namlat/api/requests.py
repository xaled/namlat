import requests
import json
import logging
logger = logging.getLogger(__name__)


def pull_request(server, last_commit_id):
    try:
        resp = requests.post(server+'/namlat/pull', data={'last_commit_id': last_commit_id})
        return json.loads(resp.text)['updates_log']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None


def update_request(server, old_commit_id, update):
    try:
        resp = requests.post(server+'/namlat/update', data={'old_commit_id': old_commit_id, 'update': json.dumps(update)})
        return json.loads(resp.text)['commit_id']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None


def sync_request(server):
    try:
        resp = requests.get(server+'/namlat/sync')
        logger.info("received %dB sync data", len(resp.content))
        resp_data = json.loads(resp.text)
        return resp_data['sync_data'], resp_data['sync_logs']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None


def create_node_request(server, address, public_key, node_name):
    try:
        resp = requests.post(server+'/namlat/createNode', data={'gw':server, 'address':address,
                                                                'public_key': public_key, 'node_name': node_name})
        logger.info("received %dB sync data", len(resp.text))
        # logger.info("received data: %s", resp.text)
        resp_data = json.loads(resp.text)
        return resp_data['accepted'], resp_data['sync_data'], resp_data['sync_logs']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None