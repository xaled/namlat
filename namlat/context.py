class NamlatContext:
    def __init__(self):
        # self.data = None
        self.secret = None
        self.rsa_key = None
        self.node_name = None
        self.config = None
        self.localdb = None
        self.data_dir = None

    def set_context(self, secret, rsa_key, node_name, config, localdb, data_dir):  # address, logs
        # self.data = data
        self.secret = secret
        self.rsa_key = rsa_key
        self.node_name = node_name
        self.config = config
        self.localdb = localdb
        self.data_dir = data_dir


context = NamlatContext()