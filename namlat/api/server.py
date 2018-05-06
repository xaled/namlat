import logging
# import json
import time
from namlat.context import context
from namlat.updates.message_server import message_server

logger = logging.getLogger(__name__)


def ping(node_name):
    if 'last_ping' not in context.localdb:
        context.localdb['last_ping'] = dict()
    context.localdb['last_ping'][node_name] = time.time()
    context.localdb.save()
    return True


def pull(node_name):
    # updates_log = dict()
    # if last_commit_id in context.localdb['logs']['commit_ids']:
    #     _index = context.localdb['logs']['commit_ids'].index(last_commit_id)
    #     updates_log['commit_ids'] = context.localdb['logs']['commit_ids'][_index+1:]
    #     updates_log['updates'] = dict()
    #     for commit_id in updates_log['commit_ids']:
    #         updates_log['updates'][commit_id] = context.localdb['logs']['updates'][commit_id]
    #     return updates_log, message_server.get_mail_bag(node_name)
    # else:
    #     return None, []
    return message_server.get_mail_bag(node_name)


def updati( outgoing_mail):
    # logger.debug("received update outgoing_mail: %s", outgoing_mail)
    for recipient in outgoing_mail:
        for message in outgoing_mail[recipient]:
            message_server.receive(message, forward=True)

    # if not update.check_signature(context.data['public_keys']):
    #     logger.warning("Bad signature")
    #     return
    # if context.localdb['logs']['commit_ids'][-1] != old_commit_id:
    #     return None
    #     # conflicts = check_conflicts(old_commit_id, update)
    #     # if len(conflicts) != 0:
    #     #     logger.warning("conflicts in update")
    #     #     report_conflicts(conflicts)
    #     #     return None  # TODOO: what to return when fail
    # commit_id = calculate_commit_id(update)
    # apply_update(update, commit_id, server=True)
    # return commit_id


def sync():
    # return context.data.db, context.localdb['logs']
    pass


# def check_conflicts(old_commit_id, update):
#     new_update = update.get_edits_dict()
#     conflicts = list()
#     updates_log = pull(old_commit_id)  #TODOO: threads & locks?
#     if updates_log is not None:
#         new_update_pathes_processed = list()
#         for e in new_update['edits']:
#             new_update_pathes_processed.append(json.dumps(e['path'])[1:-1])
#         for ci in  updates_log['updates']:
#             u = updates_log['updates'][ci]
#             for e in u['edits']:
#                 path_processed = json.dumps(e['path'])[1:-1]
#                 for pp in new_update_pathes_processed:
#                     if pp in path_processed or path_processed in pp:
#                         conflict = {'edit':new_update['edits'][new_update_pathes_processed.index(pp)],
#                                     'old_commit_id':old_commit_id, 'older_edit':e, 'older_edit_commit_id':ci}
#                         conflicts.append(conflict)
#     return conflicts

#
# def report_conflicts(conflicts):  # TODOO: (after report implementation)
#     pass


def create_node(public_key, node_name):
    # works only if there is one server/master that is jobless
    _create_node(public_key, node_name)
    return True


def create_server(public_key, node_name):
    _create_node(public_key, node_name)


def _create_node(public_key, node_name):
    # edit_data = EditDict(context.data)
    # # edit_data['inbox'][node_name] = []
    # # with context.localdb:
    # #     context.localdb['inbox'][node_name] = []
    # try:
    #     edit_data['public_keys'][node_name] = public_key.decode()
    # except:
    #     edit_data['public_keys'][node_name] = public_key
    # # edit_data['jobs'][address] = {}
    # # if gw is None:
    # #     edit_data['config'][address] = {}
    # # else:
    # #     edit_data['config'][address] = {'gw': gw}
    # edit_data['nodes'][node_name] = {'name': node_name}
    # update = Update(edit_data.edits)
    # update.sign(context.rsa_key, context.node_name)
    # commit_id = calculate_commit_id(update)
    # apply_update(update, commit_id, no_check=True, server=True)
    with context.localdb:
        if 'nodes' not in context.localdb:
            context.localdb['nodes'] = {}
        if node_name not in context.localdb['nodes']:
            context.localdb['nodes'][node_name] = {'node_name': node_name, 'public_key': public_key}