#!/usr/bin/python3
from Crypto.PublicKey import RSA
from time import sleep, time
import os
import json
import requests
import importlib
from kutils.json_min_db import JsonMinConnexion
import logging
from namlat.utils.edits_dict import EditDict
import namlat.utils as nu
import namlat.updates as nup


class NamlatContext:
    def __init__(self):
        self.data = None
        self.address = None
        self.secret = None

    def set_context(self, data, address, secret):
        self.data = data
        self.address = address
        self.secret = secret


SLEEP = 20
context = NamlatContext()
logs, data, address, rsa_key = None, None, None, None
logger = logging.getLogger(__name__)


# TODO log, info, debug, errors, except exc_info, error_report
def client_main(args):
    load_data(args)
    while True:
        pull_client()
        jobs = get_jobs()
        logger.debug("len(jobs)=%d", len(jobs))
        for job in jobs:
            logger.debug("executing job: %s", job)
            update = execute_job(job)
            job['last_executed'] = time()
            logger.debug("signing update=%s", update)
            update_signed = nup.sign_update(update, rsa_key, address)
            logger.debug("sending peer update to gw")
            update_client(update_signed)
            pull_client()
        logger.info("sleeping for %ds" % SLEEP)
        sleep(SLEEP)


def sync_main(args):
    pass


def create_main(args):
    global logs, data, address, rsa_key, context, secret
    for f in [args.data_path, args.secret_path, args.logs_path, args.cert_path]:
        if os.path.exists(f):
            if args.force_create:
                logger.warning("file %s already exists. deleting the file!")
                os.unlink(f)
            else:
                logger.error("file %s already exists",f)
                return
    private_key, public_key = nu.generate_keys()
    with open(args.cert_path,'w') as fou:
        fou.write(private_key.decode())
    rsa_key = RSA.importKey(open(args.cert_path).read())
    address = nu.public_key_address(rsa_key.publickey())
    logs = JsonMinConnexion(path=args.logs_path, template={'commit_ids': [], 'updates': {}})
    data = JsonMinConnexion(path=args.data_path, template={'jobs': {address: {}}, 'config': {address: {}},
                                                           'public_keys': {}, 'new_reports': {address: []}},)
    secret = JsonMinConnexion(path=args.secret_path, template={})
    context.set_context(data, address, secret)
    sync_client()
    update = new_namla_update(address, public_key)
    update_signed = nup.sign_update(update, rsa_key, address)
    update_client(update_signed)


def execute_job(job):
    # try:
    module_ = importlib.import_module(job['module'])
    class_ = module_.__dict__[job['class']]
    job_object = class_(job['module'], job['class'])
    # kwargs = dict()
    # for arg in job['args']: # TODO: args that can be references
    #     if arg['type'] == 'var':
    #         kwargs[arg['key']] = nu.path_to_dict(data, arg['path'], address=address)
    #     else:
    #         kwargs[arg['key']] = arg['value']
    kwargs = dict(job['args'])
    job_object.kwargs = kwargs
    job_object.init_job()
    job_object.execute()
    #job_object.finished()
    return job_object.get_update()
    # except:
    #     raise  # TODO: catch, log and continue


def get_jobs():
    jobs = list()
    for job_id in data['jobs'][address]:
        job = data['jobs'][address][job_id]
        if time() - job['last_executed'] > job['period']:
            jobs.append(job)
    return jobs


def pull_client():
    if 'gw' in data['config'][address]:
        updates_log = _pull_client_request(data['config'][address]['gw'], logs['commit_ids'][-1])
        logger.debug("pull_client received update_log: %s", updates_log)
        if updates_log is not None:
            apply_updates_log(updates_log)


def update_client(update):
    if 'gw' in data['config'][address]:
        commit_id = _update_client_request(data['config'][address]['gw'], logs['commit_ids'][-1], update)
        logger.debug("received commit_id=%s", commit_id)
        if commit_id is not None:
            apply_update(update, commit_id)
    else:
        commit_id = calculate_commit_id(update)
        apply_update(update, commit_id)


def sync_client():
    if 'gw' in data['config'][address]:
        sync_data, sync_logs = _sync_client_server(data['config'][address]['gw'])
        apply_sync_data(sync_data, sync_logs)
    else:
        logger.warning("Client doesn't have a gateway to sync from")


def _pull_client_request(server, last_commit_id):
    try:
        resp = requests.post(server+'/namlat/pull', data={'last_commit_id': last_commit_id})
        return json.loads(resp.content)['updates_log']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None


def _update_client_request(server, old_commit_id, update):
    try:
        resp = requests.post(server+'/namlat/update', data={'old_commit_id': old_commit_id, 'update': json.dumps(update)})
        return json.loads(resp.content)['commit_id']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
        return None


def _sync_client_server(server):
    try:
        resp = requests.get(server+'/namlat/sync')
        logger.info("received %dB sync data", len(resp.content))
        return json.loads(resp.content)['sync_data'], json.loads(resp.content)['sync_logs']
    except Exception as e:
        logger.error("Exception while sending pull request to server:%s", server, exc_info=True)
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


def update_server(old_commit_id, update):
    if not nup.check_signature(update, data['public_keys']):
        logger.warning("Bad signature")
        return
    if logs['commit_ids'][-1] != old_commit_id:
        conflicts = check_conflicts(old_commit_id, update)
        if len(conflicts) != 0:
            logger.warning("conflicts in update")
            report_conflicts(conflicts)
            return None  # TODO: what to return when fail
    commit_id = calculate_commit_id(update)
    apply_update(update, commit_id)
    return commit_id


def sync_server():
    return data, logs


def load_data(args):
    try:
        global logs, data, address, rsa_key, context, secret
        rsa_key = RSA.importKey(open(args.cert_path).read())
        address = nu.public_key_address(rsa_key.publickey())
        logs = JsonMinConnexion(path=args.logs_path, create=False)
        data = JsonMinConnexion(path=args.data_path, create=False)
        secret = JsonMinConnexion(path=args.secret_path, create=False)
        context.set_context(data, address, secret)
    except Exception:
        logger.error("Error loading data args=%s", args, exc_info=True)
        print("if fist time run namlat.py --create name")
        raise


def apply_sync_data(sync_data, sync_logs):
    global data, logs
    data.db.clear()
    data.db.update(sync_data)
    data.save()
    logs.db.clear()
    logs.db.update(sync_logs)
    logs.save()


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


def apply_update(update, commit_id):
    logger.debug("applying update, update=%s, commit_id=%s", update, commit_id)
    if nup.check_signature(update, data['public_keys']):
        for edit in update['edits']:
            apply_edit(edit)
    logs['commit_ids'].append(commit_id)
    logs['updates'][commit_id] = update
    logs.save()
    data.save()

def apply_updates_log(updates_log):  # TODO
    for commit_id in updates_log['commit_ids']:
        apply_update(updates_log['updates'][commit_id], commit_id)


def calculate_commit_id(update):
    if len(logs['commit_ids']) == 0:
        data_tohash = b''
    else:
        data_tohash = logs['commit_ids'][-1].encode()
    data_tohash += json.dumps(update).encode()
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


def new_namla_update(address, public_key):
    edit_data = EditDict(data)
    edit_data['new_reports'][address] = []
    edit_data['public_keys'][address] = public_key.decode()
    edit_data['jobs'][address] = {}
    edit_data['config'][address] = {}
    return nup.Update(edit_data.edits)



