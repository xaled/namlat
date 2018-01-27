import namlat
from namlat.namlat_api import server_main
from namlat.utils import DummyObject
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
dn = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(dn, "logs-server.json")
DATA_PATH = os.path.join(dn, "data-server.json")
CERT_PATH = os.path.join(dn, "private_key-server.pem")
args = DummyObject()
args.logs_path = LOGS_PATH
args.data_path = DATA_PATH
args.cert_path = CERT_PATH
server_main()
namlat.client_main(args)