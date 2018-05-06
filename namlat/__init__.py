#!/usr/bin/python3
from Crypto.PublicKey import RSA
from time import sleep, time
import os
import importlib
from xaled_utils.json_min_db import JsonMinConnexion
import logging
from namlat.context import context
from namlat.config import SLEEP
from namlat.utils.edits_dict import EditDict
# from namlat.updates import Update
import namlat.utils as nu

import namlat.api.client as client
import namlat.api.server as server

# logs, data, address, rsa_key = None, None, None, None
logger = logging.getLogger(__name__)


# TODO log, info, debug, errors, except exc_info, error_report
def client_main(args):
    load_data(args)
    while client.ping():
        client.pull()
        jobs = get_jobs()
        logger.debug("len(jobs)=%d", len(jobs))
        for job in jobs:
            logger.debug("executing job: %s (%s.%s)", job['job_id'], job['module'], job['class'])
            execute_job(job)

            # logger.debug("signing update=%s", update)
            # update.sign(context.rsa_key, context.node_name)
            logger.debug("sending peer update to gw")
            client.updati()
            client.pull()
            update_last_executed(job)
        if args.cron and not (args.server and not args.no_server_jobs):
            break
        logger.info("sleeping for %ds" % SLEEP)
        sleep(SLEEP)


def sync_main(args):
    pass
    # load_data(args)
    # if client.ping():
    #     client.sync()


def create_main(args):
    # global logs, data, address, rsa_key, context, secret

    for f in [args.secret_path, args.localdb_path, args.cert_path, args.config_path]:
        if os.path.exists(f):
            if args.force_create:
                logger.warning("file %s already exists. deleting the file!", f)
                os.unlink(f)
            else:
                print("file %s already exists! try --force-create option." % f)
                return
    private_key, public_key = nu.generate_keys()
    with open(args.cert_path, 'w') as fou:
        fou.write(private_key.decode())
    rsa_key = RSA.importKey(open(args.cert_path).read())
    if args.gw is None:
        print("What is the gateway for this node?")
        print("(keep it empty if this node is the master)")
        gw = input(":")
    else:
        gw = args.gw
    is_master = (gw == '')
    if not is_master:
        if not client.ping(gw, args.name):
            print("Server unreachable!")
            return
    # address = nu.public_key_address(rsa_key.publickey())
    # logs = JsonMinConnexion(path=args.logs_path, template={'commit_ids': [], 'updates': {}})
    # data = JsonMinConnexion(path=args.data_path, template={'nodes': {},
    #                                                        'public_keys': {}}, indent=None)
    secret = JsonMinConnexion(path=args.secret_path, template={})
    config = JsonMinConnexion(path=args.config_path, template={"jobs": {}})
    localdb = JsonMinConnexion(path=args.localdb_path, template={"jobs": {}, "is_master": is_master,
                                                                 "last_commit_id": "", 'inbox': {}}, indent=None)
    # context.set_context(data, address, secret, logs, rsa_key, args.name, config)
    context.set_context(secret, rsa_key, args.name, config, localdb, args.data_dir)

    if not is_master:
        client.create_node(gw, public_key, args.name)
        config['gw'] = gw
        config.save()
    else:
        server.create_server(public_key, args.name)


def update_last_executed(job):
    context.localdb['jobs'][job['job_id']]['last_executed'] = time()
    context.localdb.save()


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
    # job_object.finished()
    return job_object.get_update()
    # except:
    #     raise  # TODO: catch, log and continue


def get_jobs():
    jobs = list()
    for job_id in context.config['jobs']:
        job = context.config['jobs'][job_id]
        try:
            last_executed = context.localdb['jobs'][job_id]['last_executed']
        except:
            with context.localdb:
                if not 'jobs' in context.localdb:
                    context.localdb['jobs'] = {}
                context.localdb['jobs'][job_id] = {'last_executed': 0.0}
            last_executed = 0.0
        if time() - last_executed > job['period']:
            job_ = dict(job)
            job_['job_id'] = job_id
            jobs.append(job_)
    return jobs


def load_data(args):
    try:
        # global logs, data, address, rsa_key, context, secret
        rsa_key = RSA.importKey(open(args.cert_path).read())
        # address = nu.public_key_address(rsa_key.publickey())
        # logs = JsonMinConnexion(path=args.logs_path, create=False)
        # data = JsonMinConnexion(path=args.data_path, create=False, indent=None)
        secret = JsonMinConnexion(path=args.secret_path, create=False)
        config = JsonMinConnexion(path=args.config_path, create=False)
        localdb = JsonMinConnexion(path=args.localdb_path, create=False, indent=None)
        # context.set_context(data, address, secret, logs, rsa_key, args.name, config)
        context.set_context(secret, rsa_key, args.name, config, localdb, args.data_dir)
    except Exception:
        logger.error("Error loading data args=%s", args, exc_info=True)
        print("if fist time run namlat.py --create name")
        raise

# def _create_main_gw(gw):
#     context.data['config']['gw']
#     context.data.save()
#
#     client.sync()
#     update = new_namla_update(context.address, context.public_key)
#     update_signed = nup.sign_update(update, context.rsa_key, context.address)
#     update_client(update_signed)


# def new_namla_update(address, public_key):
#     edit_data = EditDict(context.data)
#     edit_data['new_reports'][address] = []
#     edit_data['public_keys'][address] = public_key.decode()
#     edit_data['jobs'][address] = {}
#     edit_data['config'][address] = {}
#     return Update(edit_data.edits)
