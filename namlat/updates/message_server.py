from namlat.context import context


class MessageServer:
    def __init__(self):
        self.outgoing_stack = list()
        self.forward_stack = list()
        self.new_messages = set()

    def send(self, message):
        self._transfer(message, True)

    def receive(self, message):
        self._transfer(message, False)

    def _transfer(self, message, outgoing):
        if len(message.recepients) == 0:
            recepients = get_message_recipients(message)
        else:
            recepients = message.recepients

        for recepient in recepients:
            if recepient[0] == context.node_name:
                # internal
                with context.localdb:
                    if recepient[1] not in context.localdb:
                        context.localdb['inbox'][recepient[1]] = list()
                    context.localdb['inbox'][recepient[1]].append(message)
                self.new_messages.add(recepient[1])
            else:
                # external
                if outgoing:
                    self.outgoing_stack.append(message)
                else:
                    self.forward_stack.append(message)


message_server = MessageServer()

def get_message_recipients(message):
    # hardcoded filtering rules  TODO:
    if message.type == 'report':
        return [('master', 'namlat.modules.report')]
    # other filtering rules:

    # else: forward to master
    return [('master', '_')]