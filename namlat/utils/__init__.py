from Crypto.Random import get_random_bytes
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
import hashlib


def sha256_digest(data):
    return hashlib.sha256(data).hexdigest()


def public_key_address(rsapubkey):
    return sha256_digest(rsapubkey.exportKey())[:16]


def commit_id(data):
    return sha256_digest(data)[:32]


# def path_to_dict(data, path, address):
#     value = data
#     for key in path:
#         if key == '{ADDRESS}':
#             key = address
#         value = value[key]
#     return value


def path_to_dict(data, path):
    value = data
    for key in path:
        value = value[key]
    return value


def sign_data(rsakey, data):
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(data)
    sign = signer.sign(digest)
    return b64encode(sign).decode()


def verify_sign(rsapubkey, signature, data):
    signer = PKCS1_v1_5.new(rsapubkey)
    digest = SHA256.new()
    digest.update(data)
    if signer.verify(digest, b64decode(signature)):
        return True
    return False


def encrypt_data(rsapubkey, data):
    session_key = get_random_bytes(16)

    cipher_rsa = PKCS1_OAEP.new(rsapubkey)
    session_key_encrypted = cipher_rsa.encrypt(session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    nonce = cipher_aes.nonce
    return session_key_encrypted, nonce, tag, ciphertext


def decrypt_data(rsakey, session_key_encrypted, nonce, tag, ciphertext):
    cipher_rsa = PKCS1_OAEP.new(rsakey)
    session_key = cipher_rsa.decrypt(session_key_encrypted)

    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return data

def generate_keys():
    rng = Random.new().read
    rsa = RSA.generate(4096, rng)

    private_key = rsa.exportKey()
    public_key = rsa.publickey().exportKey()

    return private_key, public_key



class DummyObject(object):
    pass