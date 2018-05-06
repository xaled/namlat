import requests
# import json
import xaled_utils.json_serialize as json
import logging

logger = logging.getLogger(__name__)


def ping_request(server, node_name):
    try:
        resp = requests.post(server + '/namlat/ping', data={'node_name': node_name})
        return json.loads(resp.text)['ping']
    except:
        logger.error("Exception while sending ping request to server:%s", server, exc_info=True)
        return False


def pull_request(server, node_name):
    try:
        # resp = requests.post(server+'/namlat/pull', data={'last_commit_id': last_commit_id, "node_name": node_name})
        resp = requests.post(server + '/namlat/pull', data={"node_name": node_name})
        data = json.loads(resp.text)
        # return data['updates_log'], data['mail_bag']
        return data['mail_bag']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None


def update_request(server, outgoing_mail):
    try:
        resp = requests.post(server + '/namlat/update', data={'outgoing_mail': json.dumps(outgoing_mail)})
        return resp.status_code == 200
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None


def sync_request(server):
    pass
    # try:
    #     resp = requests.get(server + '/namlat/sync')
    #     logger.info("received %dB sync data", len(resp.content))
    #     resp_data = json.loads(resp.text)
    #     return resp_data['sync_data'], resp_data['sync_logs']
    # except Exception as e:
    #     logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
    #     return None


def create_node_request(server, public_key, node_name):
    try:
        resp = requests.post(server + '/namlat/createNode', data={'gw': server,  # 'address':address,
                                                                  'public_key': public_key, 'node_name': node_name})
        # logger.info("received %dB sync data", len(resp.text))
        # logger.info("received data: %s", resp.text)
        resp_data = json.loads(resp.text)
        # return resp_data['accepted'], resp_data['sync_data'], resp_data['sync_logs']
        return resp_data['accepted']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None
