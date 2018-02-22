from Crypto.PublicKey import RSA
import logging as _logging
import json
import time
import namlat.utils as nu

logger = _logging.getLogger(__name__)


def get_update_from_request_dict(request_dict):
    edits = json.loads(request_dict['edits_json'])['edits']
    update = Update(edits)
    update.edits_json = request_dict['edits_json']
    update.signature = request_dict['signature']
    update.node_name = request_dict['node_name']
    update.signed = True
    update.checked = False
    update.check = False
    update.edit_class = False
    return update

class Update:
    def __init__(self, edits):
        self.edits = edits
        self.edits_json = None
        self.signature = None
        # self.address = None
        self.node_name = None
        self.signed = False
        self.checked = True
        self.check = True
        self.edit_class = True

    def sign(self, rsa_key, node_name):
        if not self.signed:
            self.edits_json = json.dumps(self.get_edits_dict())
            data_tosign = self.edits_json.encode()
            self.signature = nu.sign_data(rsa_key, data_tosign)
            # self.address = address
            self.node_name = node_name
            self.signed = True

    def check_signature(self, public_keys):
        if not self.checked:
            rsapubkey = RSA.importKey(public_keys[self.node_name].encode())
            data_toverify = self.edits_json.encode()
            self.check = nu.verify_sign(rsapubkey, self.signature, data_toverify)
            self.checked = True
        return self.check

    def get_request_dict(self):
        return {'node_name': self.node_name, 'signature': self.signature, 'edits_json': self.edits_json}

    def get_edits_dict(self):
        if self.edit_class:
            edits = []
            for e in self.edits:
                if isinstance(e, Edit):
                    edits.append(e.get_dict())
                else:
                    edits.append(e)
            return {'edits': edits}
        else:
            return self.edits


class Edit:
    def __init__(self, verb, path, value=None):
        self.verb = verb
        self.path = path
        self.value = value

    def get_dict(self):
        return {'verb': self.verb, 'path': self.path, 'value': self.value}




# def sign_update(update, rsa_key, address):
#     update_signed = dict()
#     update.get_dict()['edits'] = update.get_dict()['edits']
#     update_signed['edits-json'] = json.dumps(update.get_dict()['edits']) # send json dump to normalize signature check
#
#     data_tosign = update_signed['edits-json'].encode()
#     update_signed['signature'] = nu.sign_data(rsa_key, data_tosign)
#     update_signed['address'] = address
#     return update_signed


# def check_signature(update_signed, public_keys):
#     if 'checked' not in update_signed:
#         rsapubkey = RSA.importKey(public_keys[update_signed['address']].encode())
#         data_toverify = update_signed['edits-json'].encode()
#         update_signed['edits'] = json.loads(update_signed['edits-json'])
#         update_signed['checked'] = nu.verify_sign(rsapubkey, update_signed['signature'], data_toverify)
#     return update_signed['checked']
