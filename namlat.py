#!/usr/bin/python3
from time import sleep, time
import requests
import json
import logging


logger = logging.getLogger(__name__)
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
    pass  # TODO


def get_jobs():
    jobs = list()
    for job_id in data['jobs'][public_key]:
        job = data['jobs'][public_key][job_id]
        if time() - job['last_executed'] > job['period']:
            jobs.append(job)
    return jobs


def load_data():#TODO
    global logs, data, public_key, cert
    logs = None
    data = None
    public_key = None
    cert = None


def sign_update(update):#TODO
    pass

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


def check_signature(update):#TODO
    pass


def calculate_commit_id(update):
    pass


def check_conflicts(old_commit_id, update):
    return


def report_conflicts(conflicts):
    pass


def pull_client():
    if 'gw' in data['config'][public_key]:
        updates_log = _pull_client_request(data['config'][public_key]['gw'], logs['commit_ids'][-1])
        if updates_log is not None:
            apply_updates_log(updates_log)


def update_client(update):
    if 'gw' in data['config'][public_key]:
        commit_id = _update_client_request(data['config'][public_key]['gw'], logs['commit_ids'][-1], update)
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


