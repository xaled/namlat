class NamlatContext:
    def __init__(self):
        self.data = None
        self.address = None
        self.secret = None
        self.logs = None
        self.rsa_key = None
        self.node_name = None
        self.is_set = False

    def set_context(self, data, address, secret, logs, rsa_key, node_name):
        self.data = data
        self.address = address
        self.secret = secret
        self.logs = logs
        self.rsa_key = rsa_key
        self.node_name = node_name
        self.is_set = True




context = NamlatContext()