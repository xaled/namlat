from Crypto.PublicKey import RSA
import logging as _logging
import json
import namlat_utils as nu

logger = _logging.getLogger(__name__)


class Update:
    def __init__(self, edits):
        self.__dict__ = dict()
        self.__dict__['edits'] = edits


class Edit:
    def __init__(self, verb, path, value):
        self.__dict__ = dict()
        self.__dict__['verb'] = verb
        self.__dict__['path'] = path
        self.__dict__['value'] = value


def sign_update(update, rsa_key, address):
    edits = update['edits']
    data_tosign = json.dumps(edits).encode()
    update['signature'] = nu.sign_data(rsa_key, data_tosign)
    update['address'] = address
    return update


def check_signature(update, public_keys):
    rsapubkey = RSA.importKey(public_keys[update['address']].encode())
    edits = update['edits']
    data_toverify = json.dumps(edits).encode()
    return nu.verify_sign(rsapubkey, update['signature'], data_toverify)
