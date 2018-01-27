from Crypto.PublicKey import RSA
import logging as _logging
import json
import namlat.utils as nu

logger = _logging.getLogger(__name__)


class Update:
    def __init__(self, edits):
        self.edits = edits

    def get_dict(self):
        edits = []
        for e in self.edits:
            edits.append(e.get_dict())
        return {'edits': edits}


class Edit:
    def __init__(self, verb, path, value=None):
        self.verb = verb
        self.path = path
        self.value = value

    def get_dict(self):
        return {'verb': self.verb, 'path': self.path, 'value': self.value}


def sign_update(update, rsa_key, address):
    update = update.get_dict()
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