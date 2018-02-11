import logging
from namlat.context import context
from namlat.api.common import apply_update, apply_updates_log, calculate_commit_id, apply_sync_data
from namlat.api.requests import pull_request, update_request, sync_request, create_node_request, ping_request
logger = logging.getLogger(__name__)

def ping(server=None):
    if server is None:
        if 'gw' in context.config:
            return ping_request(context.confg['gw'])
        return True
    return ping_request(server)


def pull():
    if 'gw' in context.config:
        updates_log = pull_request(context.config['gw'], context.logs['commit_ids'][-1])
        logger.debug("pull_client received update_log: %s", updates_log)
        if updates_log is not None:
            apply_updates_log(updates_log)


def update(update):
    if 'gw' in context.config:
        commit_id = update_request(context.config['gw'], context.logs['commit_ids'][-1], update)
        logger.debug("received commit_id=%s", commit_id)
        if commit_id is not None:
            apply_update(update, commit_id)
    else:
        commit_id = calculate_commit_id(update)
        apply_update(update, commit_id)


def sync():
    if 'gw' in context.config:
        sync_data, sync_logs = sync_request(context.config['gw'])
        apply_sync_data(sync_data, sync_logs)
    else:
        logger.warning("Client does not have a gateway to sync from.")


def create_node(gw, public_key, node_name):
    created, sync_data, sync_logs = create_node_request(gw, public_key, node_name)
    apply_sync_data(sync_data, sync_logs)