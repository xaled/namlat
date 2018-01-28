import logging
from namlat.context import context
from namlat.api.common import apply_update, apply_updates_log, calculate_commit_id, apply_sync_data
from namlat.api.requests import pull_request, update_request, sync_request, create_node_request
logger = logging.getLogger(__name__)


def pull():
    if 'gw' in context.data['config'][context.address]:
        updates_log = pull_request(context.data['config'][context.address]['gw'],
                                           context.logs['commit_ids'][-1])
        logger.debug("pull_client received update_log: %s", updates_log)
        if updates_log is not None:
            apply_updates_log(updates_log)


def update(update):
    if 'gw' in context.data['config'][context.address]:
        commit_id = update_request(context.data['config'][context.address]['gw'],
                                           context.logs['commit_ids'][-1], update)
        logger.debug("received commit_id=%s", commit_id)
        if commit_id is not None:
            apply_update(update, commit_id)
    else:
        commit_id = calculate_commit_id(update)
        apply_update(update, commit_id)


def sync():
    if 'gw' in context.data['config'][context.address]:
        sync_data, sync_logs = sync_request(context.data['config'][context.address]['gw'])
        apply_sync_data(sync_data, sync_logs)
    else:
        logger.warning("Client does not have a gateway to sync from.")


def create_node(gw, address, public_key, node_name):
    created, sync_data, sync_logs = create_node_request(gw, address, public_key, node_name)
    apply_sync_data(sync_data, sync_logs)