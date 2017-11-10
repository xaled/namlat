#!/usr/bin/python3
from time import sleep, time
from flask import Flask, url_for, Response, json
import logging
logger = logging.getLogger(__name__)

SLEEP=3600






def run_flask_service():#TODO
    global app
    app = Flask(__name__)
    app.run()

@app.route('/hello', methods = ['GET'])
def api_hello():
    data = {
        'hello'  : 'world',
        'number' : 3
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://luisrei.com'

    return resp



def client_main():
    load_data()
    while True:
        sleep(SLEEP)
        pull_client()
        jobs = get_jobs()
        for job in jobs:
            updates = execute_job(job)
            updates_signed = sign_updates(updates)
            update_client(updates_signed)
            pull_client()


def execute_job(job):
    pass#TODO

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

def sign_updates(updates):#TODO
    pass

def apply_updates(updates):#TODO
    check_signature()
    #apply

def check_signature():#TODO
    pass

def pull_client():
    updates_log = _pull_client_request() #TODO
    if updates_log is None or len(updates_log['commit_ids']) == 0:
        return
    for commit_id in updates_log['commit_ids']:
        apply_updates(updates_log['updates'][commit_id])

def update_client(updates):
    _update_client_request() #TODO

def pull_server(last_commit_id):
    # TODO threadproof
    updates_log = dict()
    if last_commit_id in  logs['commit_ids']:
        _index = logs['commit_ids'].index(last_commit_id)
        updates_log['commit_ids'] = logs['commit_ids'][_index+1:]
        updates_log['updates'] = dict()
        for commit_id in updates_log['commit_ids']:
            updates_log['updates'][commit_id] = logs['updates'][commit_id]
        return updates_log
    else:
        return None

def update_server(old_commit_id, updates): #TODO
    #TODO threadproof
    check_signature()
    if logs['commit_ids'][-1] != old_commit_id:
        conflicts = check_conflicts(old_commit_id, updates)
        if len(conflicts) != 0:
            report_conflicts(conflicts)
            return None# TODO: what to return when fail
    commit_id = calculate_commit_id(updates)
    apply_updates(old_commit_id, commit_id, updates)
    return commit_id

