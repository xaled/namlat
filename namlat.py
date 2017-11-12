#!/usr/bin/python3
from time import sleep, time
import os
import requests
import json
import importlib
from Crypto.PublicKey import RSA
from kutils.json_min_db import JsonMinConnexion
import logging
import namlat_utils as nu




logger = logging.getLogger(__name__)
dn = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(dn,"logs.json")
DATA_PATH = os.path.join(dn,"data.json")
CERT_PATH = os.path.join(dn,"private_key.pem")
SLEEP = 3600


# TODO log, info, debug, errors, except exc_info, error_report
def client_main():
    load_data()
    while True:
        sleep(SLEEP)
        pull_client()
        jobs = get_jobs()
        for job in jobs:
            update = execute_job(job)
            update_signed = sign_update(update)
            update_client(update_signed)
            pull_client()


def execute_job(job):
    try:
        module = importlib.import_module(job['module'])
        kwargs = dict()
        for arg in job['args']:
            if arg['type'] == 'var':
                kwargs[arg['key']] = nu.path_to_dict(data, arg['path'], address=address)
            else:
                kwargs[arg['key']] = arg['value']
        return module.execute(**kwargs)
    except:
        return None  # TODO: log


def get_jobs():
    jobs = list()
    for job_id in data['jobs'][address]:
        job = data['jobs'][address][job_id]
        if time() - job['last_executed'] > job['period']:
            jobs.append(job)
    return jobs


def load_data():#TODO
    global logs, data, address, rsa_key
    rsa_key = RSA.import_key(open(CERT_PATH).read())
    address = nu.public_key_address(rsa_key.publickey())
    logs = JsonMinConnexion(path=LOGS_PATH, template={'commit_ids':[], 'updates':{}})
    data = JsonMinConnexion(path=DATA_PATH, template={'jobs':{address:{}}, 'config':{address:{}}, 'public_keys':{}})


def sign_update(update):
    edits = update['edits']
    data_tosign = json.dumps(edits).encode()
    update['signature'] = nu.sign_data(rsa_key, data_tosign)
    update['address'] = address
    return update


def check_signature(update):#TODO
    rsapubkey = RSA.import_key(data['public_keys'][update['address']].encode())
    edits = update['edits']
    data_toverify = json.dumps(edits).encode()
    return nu.verify_sign(rsapubkey, update['signature'] , data_toverify)


def apply_edit(edit):#TODO
    pass


def apply_update(update):
    if check_signature(update):
        for edit in update['edits']:
            apply_edit(edit)
    logs['commit_ids'].append(update['commit_id'])
    logs['updates'][update['commit_id']] = update


def apply_updates_log(updates_log):#TODO
    for commit_id in updates_log['commit_ids']:
        apply_update(updates_log['updates'][commit_id])


def calculate_commit_id(update):
    pass


def check_conflicts(old_commit_id, update):
    return


def report_conflicts(conflicts):
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
        resp = requests.post(server+'/namlat/updates', data={'old_commit_id': old_commit_id, 'update':update})
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
    if not check_signature(update):
        return  # TODO: log!
    if logs['commit_ids'][-1] != old_commit_id:
        conflicts = check_conflicts(old_commit_id, update)
        if len(conflicts) != 0:
            report_conflicts(conflicts)
            return None# TODO: what to return when fail
    commit_id = calculate_commit_id(update)
    apply_update(commit_id, update)
    return commit_id


