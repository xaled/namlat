import json
import logging
from namlat.context import context
from namlat.utils import commit_id, path_to_dict
from namlat.updates import check_signature, Update
from namlat.utils.edits_dict import EditDict

logger = logging.getLogger(__name__)

def apply_sync_data(sync_data, sync_logs):
    # global data, logs
    context.data.db.clear()
    context.data.db.update(sync_data)
    context.data.save()
    context.logs.db.clear()
    context.logs.db.update(sync_logs)
    context.logs.save()


def calculate_commit_id(update):
    if len(context.logs['commit_ids']) == 0:
        data_tohash = b''
    else:
        data_tohash = context.logs['commit_ids'][-1].encode()
    data_tohash += json.dumps(update).encode()
    return commit_id(data_tohash)


def apply_updates_log(updates_log):  # TODO
    for commit_id in updates_log['commit_ids']:
        apply_update(updates_log['updates'][commit_id], commit_id)
        

def apply_update(update, commit_id, no_check=False):
    logger.debug("applying update, update=%s, commit_id=%s", update, commit_id)
    if no_check or check_signature(update, context.data['public_keys']):
        for edit in update['edits']:
            apply_edit(edit)
        context.logs['commit_ids'].append(commit_id)
        context.logs['updates'][commit_id] = update
        context.logs.save()
        context.data.save()







def apply_edit(edit):  # TODO: transaction pattern
    verb, path, value = edit['verb'], edit['path'], edit['value']
    try:
        parent = path_to_dict(context.data, path[:-1], context.address)
        key = path[-1]
        try: old_value = parent[key]
        except: old_value = None
    except:
        return  # TODO: log
    try:
        if verb == 'set':
            parent[key] = value
        elif verb == 'del':
            if key in parent:
                del parent[key]
        elif verb == 'append':
            if isinstance(old_value, list):
                parent[key].append(value)
            elif old_value is None:
                parent[key] = [value]
            else:
                raise ValueError("Object to append to is not a list")
        elif verb == 'extend':
            if isinstance(old_value, list):
                parent[key].extend(value)
            elif old_value is None:
                parent[key] = list(value)
            else:
                raise ValueError("Object to extend to is not a list")
        elif verb == 'update':
            if isinstance(old_value, dict):
                parent[key].update(value)
            elif old_value is None:
                parent[key] = dict(value)
            else:
                raise ValueError("Object to update is not a dict")
        elif verb == 'insert':
            if isinstance(old_value, list):
                parent.insert(key, value)
            else:
                raise ValueError("Object to insert into is not a list")
        elif verb == 'remove':
            if isinstance(old_value, list):
                if value in old_value:
                    parent[key].remove(value)
            elif old_value is None:
                parent[key] = list()
            else:
                raise ValueError("Object to remove from is not a list")
        elif verb == 'remove-items':
            if isinstance(old_value, list):
                for item in value:
                    if item in old_value:
                        parent[key].remove(item)
            elif old_value is None:
                parent[key] = list()
            else:
                raise ValueError("Object to remove from is not a list")
        elif verb == 'remove-keys':
            if isinstance(old_value, list):
                for k in value:
                    if k in old_value:
                        del parent[key][k]
            elif old_value is None:
                parent[key] = dict()
            else:
                raise ValueError("Object to remove from is not a dict")
        elif verb == 'clear':
            if key in parent:
                parent[key].clear()
        else:
            pass  # TODO: log
    except:
        return  # TODO: log
