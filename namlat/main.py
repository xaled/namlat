import argparse
import os
import sys
from xaled_utils.lockfile import pidlock, release_lock, LockHeld
from xaled_utils.logs import configure_logging
from xaled_utils.threads import threaded
import namlat
from namlat.api.flask import server_main
from namlat.config import DATA_DIR, VERSION


def main():
    parser = argparse.ArgumentParser(description='namlat - Decentralized monitoring and tasks')
    parser.add_argument('--version', action="store_true", default=False)
    parser.add_argument('-s', '--server', action="store_true", default=False)
    parser.add_argument('-y', '--sync', action="store_true", default=False)
    parser.add_argument('--create', action="store_true", default=False)
    parser.add_argument('-f', '--force-create', action="store_true", default=False)
    parser.add_argument('--no-server-jobs', action="store_true", default=False)
    parser.add_argument('-C', '--cron', action="store_true", default=False)
    parser.add_argument('-d', '--debug', action="store_true", default=False)
    parser.add_argument('-n','--name', action="store", default=None)
    parser.add_argument('--gw', action="store", default=None)
    # parser.add_argument('--logs-path', action="store", default=None)
    parser.add_argument('--cert-path', action="store", default=None)
    # parser.add_argument('--data-path', action="store", default=None)
    parser.add_argument('--config-path', action="store", default=None)
    parser.add_argument('--secret-path', action="store", default=None)
    parser.add_argument('--localdb-path', action="store", default=None)
    parser.add_argument('--lock-path', action="store", default=None)
    parser.add_argument('-D', '--data-dir', action="store", default=None)

    args = parser.parse_args()

    if args.version:
        print('namlat', VERSION)
        sys.exit(0)

    if args.name is None:
        parser.print_help(sys.stderr)
        print(sys.argv[0] + ': error: the following arguments are required: -n/--name')
        sys.exit(1)

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
    # if args.data_path is None:
    #     args.data_path = os.path.join(args.data_dir, "data.json")
    if args.cert_path is None:
        args.cert_path = os.path.join(args.data_dir, "private_key.pem")
    if args.secret_path is None:
        args.secret_path = os.path.join(args.data_dir, "secret.json")
    if args.config_path is None:
        args.config_path = os.path.join(args.data_dir, "config.json")
    if args.lock_path is None:
        args.lock_path = os.path.join(args.data_dir, "%s.lock"%args.name)

    if args.debug:
        configure_logging(level="DEBUG", modules=["xaled_utils", "namlat", "werkzeug", "namlat_ext"])
    else:
        configure_logging(level="INFO", modules=["xaled_utils", "namlat", "werkzeug", "namlat_ext"])
    try:
        pidlock(args.lock_path)
        if not args.sync and not args.create and not args.server:
            namlat.client_main(args)
        elif args.server:
            if not args.no_server_jobs:
                threaded(namlat.client_main, (args,), daemon=True)
            server_main(args)
        elif args.sync:
            namlat.sync_main(args)
        elif args.create:
            namlat.create_main(args)
    except LockHeld:
        print("There is already an instance of this node")
    finally:
        release_lock(args.lock_path)
