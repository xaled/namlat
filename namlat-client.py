import namlat
import os
from namlat.utils import DummyObject
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
dn = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(dn, "logs-client.json")
DATA_PATH = os.path.join(dn, "data-client.json")
CERT_PATH = os.path.join(dn, "private_key-client.pem")
args = DummyObject()
args.logs_path = LOGS_PATH
args.data_path = DATA_PATH
args.cert_path = CERT_PATH
namlat.client_main(args)