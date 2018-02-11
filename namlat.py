#!/usr/bin/python3
import argparse
import logging
import os
from kutils.lockfile import pidlock, release_lock, LockHeld
import namlat
from namlat.api.flask import server_main
from namlat.config import DATA_DIR

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='namlat - Decentralized monitoring and tasks')

    parser.add_argument('-s', '--server', action="store_true", default=False)
    parser.add_argument('-y', '--sync', action="store_true", default=False)
    parser.add_argument('-c', '--create', action="store_true", default=False)
    parser.add_argument('-f', '--force-create', action="store_true", default=False)
    parser.add_argument('-C', '--cron', action="store_true", default=False)
    parser.add_argument('-d', '--debug', action="store_true", default=False)
    parser.add_argument('-n','--name', action="store", required=True)
    # parser.add_argument('--logs-path', action="store", default=None)
    parser.add_argument('--cert-path', action="store", default=None)
    parser.add_argument('--data-path', action="store", default=None)
    parser.add_argument('--config-path', action="store", default=None)
    parser.add_argument('--secret-path', action="store", default=None)
    parser.add_argument('--localdb-path', action="store", default=None)
    parser.add_argument('--lock-path', action="store", default=None)
    parser.add_argument('-D', '--data-dir', action="store", default=None)

    args = parser.parse_args()

    # if args.data_dir is None:
    #     args.data_dir = os.path.dirname(os.path.realpath(__file__))
    # LOGS_PATH = os.path.join(dn, "logs-server.json")
    # DATA_PATH = os.path.join(dn, "data-server.json")
    # CERT_PATH = os.path.join(dn, "private_key-server.pem")
    # args = DummyObject()
    if args.data_dir is None:
        args.data_dir = os.path.join(DATA_DIR, args.name)
    if not os.path.exists(args.data_dir):
        os.makedirs(args.data_dir)
    if args.localdb_path is None:
        args.localdb_path = os.path.join(args.data_dir, "localdb.json")
    # if args.logs_path is None:
    #     args.logs_path = os.path.join(args.data_dir, "logs.json")
    if args.data_path is None:
        args.data_path = os.path.join(args.data_dir, "data.json")
    if args.cert_path is None:
        args.cert_path = os.path.join(args.data_dir, "private_key.pem")
    if args.secret_path is None:
        args.secret_path = os.path.join(args.data_dir, "secret.json")
    if args.config_path is None:
        args.config_path = os.path.join(args.data_dir, "config.json")
    if args.lock_path is None:
        args.lock_path = os.path.join(args.data_dir, "%s.lock"%args.name)
    # if args.logs_path is None:
    #     args.logs_path = os.path.join(args.data_dir, "logs-%s.json"%args.name)
    # if args.data_path is None:
    #     args.data_path = os.path.join(args.data_dir, "data-%s.json"%args.name)
    # if args.cert_path is None:
    #     args.cert_path = os.path.join(args.data_dir, "private_key-%s.pem"%args.name)
    # if args.secret_path is None:
    #     args.secret_path = os.path.join(args.data_dir, "secret-%s.json"%args.name)
    # if args.config_path is None:
    #     args.config_path = os.path.join(args.data_dir, "config-%s.json"%args.name)
    # if args.lock_path is None:
    #     args.lock_path = os.path.join(args.data_dir, "%s.lock"%args.name)




    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        pidlock(args.lock_path)
        if not args.sync and not args.create and not args.server:
            namlat.client_main(args)
        elif args.server:
            server_main(args)
        elif args.sync:
            namlat.sync_main(args)
        elif args.create:
            namlat.create_main(args)
        release_lock(args.lock_path)
    except LockHeld:
        print("There is already an instance of this node")