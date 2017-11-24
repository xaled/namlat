#!/usr/bin/python3
from Crypto.PublicKey import RSA
from time import sleep, time
import os
import json
import requests
import importlib
from kutils.json_min_db import JsonMinConnexion
import logging
import namlat_utils as nu
import namlat_updates as nup


logger = logging.getLogger(__name__)
dn = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(dn, "logs.json")
DATA_PATH = os.path.join(dn, "data.json")
CERT_PATH = os.path.join(dn, "private_key.pem")
SLEEP = 3600
context = None
logs, data, address, rsa_key = None, None, None, None


# TODO log, info, debug, errors, except exc_info, error_report
def client_main():
    load_data()
    while True:
        sleep(SLEEP)
        pull_client()
        jobs = get_jobs()
        for job in jobs:
            update = execute_job(job)
            update_signed = nup.sign_update(update, rsa_key, address)
            update_client(update_signed)
            pull_client()


def execute_job(job):
    try:
        module_ = importlib.import_module(job['module'])
        kwargs = dict()
        for arg in job['args']:
            if arg['type'] == 'var':
                kwargs[arg['key']] = nu.path_to_dict(data, arg['path'], address=address)
            else:
                kwargs[arg['key']] = arg['value']
        return module_.execute(**kwargs)
    except:
        return None  # TODO: log


def get_jobs():
    jobs = list()
    for job_id in data['jobs'][address]:
        job = data['jobs'][address][job_id]
        if time() - job['last_executed'] > job['period']:
            jobs.append(job)
    return jobs


def load_data():
    global logs, data, address, rsa_key, context
    rsa_key = RSA.importKey(open(CERT_PATH).read())
    address = nu.public_key_address(rsa_key.publickey())
    logs = JsonMinConnexion(path=LOGS_PATH, template={'commit_ids': [], 'updates': {}})
    data = JsonMinConnexion(path=DATA_PATH, template={'jobs': {address: {}}, 'config': {address: {}}, 'public_keys': {},
                                                      'new_reports': {address: []}})
    context = NamlatContext(data, address)


def apply_edit(edit):  # TODO: transaction pattern
    verb, path, value = edit['verb'], edit['path'], edit['value']
    try:
        parent = nu.path_to_dict(data, path[:-1], address)
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
        else:
            pass  # TODO: log
    except:
        return  # TODO: log


def apply_update(update, commit_id):
    if nup.check_signature(update, data['public_keys']):
        for edit in update['edits']:
            apply_edit(edit)
    logs['commit_ids'].append(commit_id)
    logs['updates'][update['commit_id']] = update


def apply_updates_log(updates_log):  # TODO
    for commit_id in updates_log['commit_ids']:
        apply_update(updates_log['updates'][commit_id], commit_id)


def calculate_commit_id(update):
    data_tohash = logs['commit_ids'][-1].encode() + json.dumps(update).encode()
    return nu.commit_id(data_tohash)


def check_conflicts(old_commit_id, new_update):
    conflicts = list()
    updates_log = pull_server(old_commit_id)  #TODO: threads & locks?
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


def pull_client():
    if 'gw' in data['config'][address]:
        updates_log = _pull_client_request(data['config'][address]['gw'], logs['commit_ids'][-1])
        if updates_log is not None:
            apply_updates_log(updates_log)


def update_client(update):
    if 'gw' in data['config'][address]:
        commit_id = _update_client_request(data['config'][address]['gw'], logs['commit_ids'][-1], update)
        if commit_id is not None:
            apply_update(commit_id, update)
    else:
        commit_id = calculate_commit_id(update)
        apply_update(commit_id, update)


def _pull_client_request(server, last_commit_id):
    try:
        resp = requests.post(server+'/namlat/pull', data={'last_commit_id': last_commit_id})
        return json.loads(resp.content)['updates_log']
    except:
        return None


def _update_client_request(server, old_commit_id, update):
    try:
        resp = requests.post(server+'/namlat/updates', data={'old_commit_id': old_commit_id, 'update': update})
        return json.loads(resp.content)['commit_id']
    except:
        return None


def pull_server(last_commit_id):
    updates_log = dict()
    if last_commit_id in logs['commit_ids']:
        _index = logs['commit_ids'].index(last_commit_id)
        updates_log['commit_ids'] = logs['commit_ids'][_index+1:]
        updates_log['updates'] = dict()
        for commit_id in updates_log['commit_ids']:
            updates_log['updates'][commit_id] = logs['updates'][commit_id]
        return updates_log
    else:
        return None


def update_server(old_commit_id, update):  # TODO
    if not nup.check_signature(update, data['public_keys']):
        return  # TODO: log!
    if logs['commit_ids'][-1] != old_commit_id:
        conflicts = check_conflicts(old_commit_id, update)
        if len(conflicts) != 0:
            report_conflicts(conflicts)
            return None  # TODO: what to return when fail
    commit_id = calculate_commit_id(update)
    apply_update(commit_id, update)
    return commit_id


class NamlatContext:
    def __init__(self):
        self.data = None
        self.address = None

    def set_context(self, data, address):
        self.data = data
        self.address = address

