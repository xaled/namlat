import time
import uuid
from xaled_utils.json_serialize import JsonSerializable
from xaled_utils.time_ops import epoch_to_iso8601
from namlat.updates.message_server import message_server


class Message(JsonSerializable):
    def __init__(self, sender, recipients, type, content, timestamp=None, uuid_=None):
        self.sender = sender
        self.recipients = recipients
        self.type = type
        self.content = content
        if timestamp is None:
            self.timestamp = time.time()
        else:
            self.timestamp = timestamp
        if uuid_ is None:
            self.uuid_ = uuid.uuid4().hex
        else:
            self.uuid_ = uuid_

    # def get_dict(self):
    #     return dict(self.__dict__)

    # def send(self, inboxpointer):
    def send(self):
        message_server.send(self)
        # if self.to_node not in inboxpointer:
        #     inboxpointer[self.to_node] = list()
        # inboxpointer[self.to_node].append(self.get_dict

    def copy(self, recipient=None):
        if recipient is None:
            return Message(self.sender, self.recipients, self.type, self.content, self.timestamp, self.uuid_)
        else:
            return Message(self.sender, [recipient], self.type, self.content, self.timestamp, self.uuid_)

    def __str__(self):
        return "Message(%s, from:%s, to:%s, type:%s, %s)" % (self.uuid_, self.sender, self.recipients, self.type,
                                                         epoch_to_iso8601(self.timestamp))
