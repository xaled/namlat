import time
from namlat.updates.message_server import message_server

class Message:
    def __init__(self, from_node, from_module, to_node, to_module, type, content):
        self.from_node = from_node
        self.from_module = from_module
        self.to_node = to_node
        self.to_module = to_module
        self.type = type
        self.content = content
        self.timestamp = time.time()

    def get_dict(self):
        return dict(self.__dict__)

    # def send(self, inboxpointer):
    def send(self, inboxpointer):
        message_server.send(self)
        # if self.to_node not in inboxpointer:
        #     inboxpointer[self.to_node] = list()
        # inboxpointer[self.to_node].append(self.get_dict())
