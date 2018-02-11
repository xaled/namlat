import logging
import json
from namlat.context import context
from namlat.api.common import apply_update, calculate_commit_id
from namlat.utils.edits_dict import EditDict
from namlat.updates import Update

logger = logging.getLogger(__name__)


def pull(last_commit_id):
    updates_log = dict()
    if last_commit_id in context.logs['commit_ids']:
        _index = context.logs['commit_ids'].index(last_commit_id)
        updates_log['commit_ids'] = context.logs['commit_ids'][_index+1:]
        updates_log['updates'] = dict()
        for commit_id in updates_log['commit_ids']:
            updates_log['updates'][commit_id] = context.logs['updates'][commit_id]
        return updates_log
    else:
        return None


def updati(old_commit_id, update):
    if not update.check_signature(context.data['public_keys']):
        logger.warning("Bad signature")
        return
    if context.logs['commit_ids'][-1] != old_commit_id:
        conflicts = check_conflicts(old_commit_id, update)
        if len(conflicts) != 0:
            logger.warning("conflicts in update")
            report_conflicts(conflicts)
            return None  # TODO: what to return when fail
    commit_id = calculate_commit_id(update)
    apply_update(update, commit_id)
    return commit_id


def sync():
    return context.data.db, context.logs.db


def check_conflicts(old_commit_id, update):
    new_update = update.get_edits_dict()
    conflicts = list()
    updates_log = pull(old_commit_id)  #TODO: threads & locks?
    if updates_log is not None:
        new_update_pathes_processed = list()
        for e in new_update['edits']:
            new_update_pathes_processed.append(json.dumps(e['path'])[1:-1])
        for ci in  updates_log['updates']:
            u = updates_log['updates'][ci]
            for e in u['edits']:
                path_processed = json.dumps(e['path'])[1:-1]
                for pp in new_update_pathes_processed:
                    if pp in path_processed or path_processed in pp:
                        conflict = {'edit':new_update['edits'][new_update_pathes_processed.index(pp)],
                                    'old_commit_id':old_commit_id, 'older_edit':e, 'older_edit_commit_id':ci}
                        conflicts.append(conflict)
    return conflicts


def report_conflicts(conflicts):  # TODO: (after report implementation)
    pass


def create_node(public_key, node_name):
    # TODO works only if there is one server/master that is jobless
    _create_node(public_key, node_name)
    return True


def create_server(public_key, node_name):
    _create_node(public_key, node_name)


def _create_node(public_key, node_name):
    edit_data = EditDict(context.data)
    edit_data['new_reports'][node_name] = []
    try:
        edit_data['public_keys'][node_name] = public_key.decode()
    except:
        edit_data['public_keys'][node_name] = public_key
    # edit_data['jobs'][address] = {}
    # if gw is None:
    #     edit_data['config'][address] = {}
    # else:
    #     edit_data['config'][address] = {'gw': gw}
    edit_data['nodes'][node_name] = {'name': node_name}
    update = Update(edit_data.edits)
    update.sign(context.rsa_key, context.node_name)
    commit_id = calculate_commit_id(update)
    apply_update(update, commit_id, no_check=True)