#!/usr/bin/python3
import argparse
import os
import logging

import namlat
from namlat.namlat_api import server_main
from namlat.utils import DummyObject


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='namlat - Decentralized monitoring and tasks')

    parser.add_argument('-s', '--server', action="store_true", default=False)
    parser.add_argument('-y', '--sync', action="store_true", default=False)
    parser.add_argument('-c', '--create', action="store_true", default=False)
    parser.add_argument('-f', '--force-create', action="store_true", default=False)
    parser.add_argument('-d', '--debug', action="store_true", default=False)
    parser.add_argument('-n','--name', action="store", required=True)
    parser.add_argument('-L','--logs-path', action="store", default=None)
    parser.add_argument('-C','--cert-path', action="store", default=None)
    parser.add_argument('-D','--data-path', action="store", default=None)
    parser.add_argument('-S','--secret-path', action="store", default=None)
    parser.add_argument('--data-dir', action="store", default=None)

    args = parser.parse_args()

    if args.data_dir is None:
        args.data_dir = os.path.dirname(os.path.realpath(__file__))
    # LOGS_PATH = os.path.join(dn, "logs-server.json")
    # DATA_PATH = os.path.join(dn, "data-server.json")
    # CERT_PATH = os.path.join(dn, "private_key-server.pem")
    # args = DummyObject()
    if args.logs_path is None:
        args.logs_path = os.path.join(args.data_dir, "logs-%s.json"%args.name)
    if args.data_path is None:
        args.data_path = os.path.join(args.data_dir, "data-%s.json"%args.name)
    if args.cert_path is None:
        args.cert_path = os.path.join(args.data_dir, "private_key-%s.pem"%args.name)
    if args.secret_path is None:
        args.secret_path = os.path.join(args.data_dir, "secret-%s.json"%args.name)


    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.sync and not args.create:
        if args.server:
            server_main()
        namlat.client_main(args)
    elif args.sync:
        namlat.sync_main(args)
    elif args.create:
        namlat.create_main(args)