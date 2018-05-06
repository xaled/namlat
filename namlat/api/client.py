import logging
from namlat.context import context
from namlat.api.common import apply_update, apply_updates_log, calculate_commit_id, apply_sync_data
from namlat.api.requests import pull_request, update_request, sync_request, create_node_request, ping_request
from namlat.updates.message_server import message_server
logger = logging.getLogger(__name__)


def ping(server=None, node_name=None):
    if node_name is None:
        node_name = context.node_name
    if server is None:
        if 'gw' in context.config:
            return ping_request(context.config['gw'], node_name)
        return True
    return ping_request(server, node_name)


def pull():
    if 'gw' in context.config:
        # updates_log, mail_bag = pull_request(context.config['gw'], context.localdb['last_commit_id'], context.node_name)
        mail_bag = pull_request(context.config['gw'], context.node_name)
        # logger.debug("pull_client received update_log: %s, mail_bag: %s", updates_log, mail_bag)
        logger.debug("pull_client received mail_bag: %s", mail_bag)
        for message in mail_bag:
            message_server.receive(message, forward=False)
        # if updates_log is not None:
        #     apply_updates_log(updates_log)
        # else:
        #     sync() #


def updati():
    if 'gw' in context.config:
        # commit_id = update_request(context.config['gw'], context.localdb['last_commit_id'],
        #                            update, message_server.get_outgoing_mail())
        update_request(context.config['gw'],  message_server.get_outgoing_mail())
        # logger.debug("received commit_id=%s", commit_id)
    #     if commit_id is not None:
    #         apply_update(update, commit_id)
    #     else:
    #         pass  # ignore job
    # else:
    #     commit_id = calculate_commit_id(update)
    #     apply_update(update, commit_id, server=True)


def sync():
    pass
    # if 'gw' in context.config:
    #     sync_data, sync_logs = sync_request(context.config['gw'])
    #     apply_sync_data(sync_data, sync_logs)
    # # else:
    #     logger.warning("Client does not have a gateway to sync from.")


def create_node(gw, public_key, node_name):
    # created, sync_data, sync_logs = create_node_request(gw, public_key, node_name)
    created = create_node_request(gw, public_key, node_name)
    # apply_sync_data(sync_data, sync_logs)
    return created