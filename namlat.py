import namlat
import os
import logging

logger = logging.getLogger(__name__)
dn = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(dn, "logs.json")
DATA_PATH = os.path.join(dn, "data.json")
CERT_PATH = os.path.join(dn, "private_key.pem")
args = object()
args.logs_path = LOGS_PATH
args.data_path = DATA_PATH
args.cert_path = CERT_PATH
namlat.client_main(args)