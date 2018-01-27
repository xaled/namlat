from __future__ import print_function
from Crypto import Random
from Crypto.PublicKey import RSA
PRIVATE_KEY_FILE = 'private_key.pem'
PUBLIC_KEY_FILE = 'public_key.pem'


if __name__ == "__main__":
    rng = Random.new().read
    rsa = RSA.generate(4096, rng)

    private_key = rsa.exportKey()
    public_key = rsa.publickey().exportKey()

    with open(PRIVATE_KEY_FILE, 'w') as fou:
        print("writing private key to:", PRIVATE_KEY_FILE)
        fou.write(private_key)

    with open(PUBLIC_KEY_FILE, 'w') as fou:
        print("writing public key to:", PUBLIC_KEY_FILE)
        fou.write(public_key)

