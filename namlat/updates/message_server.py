from namlat.context import context
import importlib
from threading import Lock
import logging
logger = logging.getLogger(__name__)


class MessageServer:
    def __init__(self):
        # self.outgoing_stack = list()
        # self.outgoing_lock = Lock()
        self.forward_stack = dict()
        self.forward_lock = Lock()
        self.new_messages = set()
        self.new_messages_lock = Lock()

    def send(self, message):
        logger.debug("sending a message: %s.", message)
        self._transfer(message)

    def receive(self, message, forward=False):
        logger.debug("receiving a message: %s.", message)
        self._transfer(message, forward=forward)

    def _transfer(self, message, forward=True):
        if len(message.recipients) == 0:
            recipients = get_message_recipients(message)
            if len(recipients) == 0:
                # External Central routing
                logger.debug("Storing the message in forward_stack before forwarding it to gateway")
                recipient = 'server'
                if forward:
                    # with self.outgoing_lock:
                        #     self.outgoing_stack.append(message)  # multiple append?
                    with self.forward_lock:
                        if not recipient in self.forward_stack:
                            self.forward_stack[recipient] = list()
                        self.forward_stack[recipient].append(message)
                else:  # ignore?
                    logger.info("Could not forward the message to %s!", recipient)
                return
        else:
            recipients = message.recipients

        for recipient in recipients:
            message_copy = message.copy(recipient)
            if recipient[0] == context.node_name:
                logger.debug("Delevering the message locally to  module: %s", recipient[1])
                # internal
                with context.localdb:
                    if 'inbox' not in context.localdb:
                        context.localdb['inbox'] = dict()
                    if recipient[1] not in context.localdb['inbox']:
                        context.localdb['inbox'][recipient[1]] = dict()
                    context.localdb['inbox'][recipient[1]][message_copy.uuid_] = message_copy
                with self.new_messages_lock:
                    self.new_messages.add(recipient[1])
            else:
                # external (local routing)
                logger.debug("Storing the message in forward_stack before forwarding it to: %s", recipient)
                if forward:
                    # with self.outgoing_lock:
                        #     self.outgoing_stack.append(message)  # multiple append?
                    with self.forward_lock:
                        if not recipient[0] in self.forward_stack:
                            self.forward_stack[recipient[0]] = list()
                        self.forward_stack[recipient[0]].append(message_copy)
                else:  # ignore?
                    logger.info("Could not forward the message to %s!", recipient)

        # call modules hooks
        self.call_modules_hooks()

    def call_modules_hooks(self):
        with self.new_messages_lock:
            for module_name in self.new_messages:
                module_ = importlib.import_module(module_name)
                if 'mail_hook' in module_.__dict__ and callable(module_.__dict__['mail_hook']):
                    logger.debug("calling mail_hook from module: %s." % module_name)
                    module_.__dict__['mail_hook']()

            self.new_messages.clear()

    def get_mail_bag(self, node_name):  # server
        if node_name in self.forward_stack:
            with self.forward_lock:
                ret = list(self.forward_stack[node_name])
                self.forward_stack[node_name].clear()
            if len(ret) > 0:
                logger.info("Forwarding %d message to %s.", len(ret), node_name)
                return ret
        logger.debug("No message to forward to %s.", node_name)
        return []

    def get_outgoing_mail(self):  # client
        with self.forward_lock:
            ret = dict(self.forward_stack)
            self.forward_stack.clear()
        logger.info("Forwarding %d outgoing message to gateway.", len(ret))
        return ret


message_server = MessageServer()


def get_message_recipients(message):
    # hardcoded filtering rules  TODO: Routage, explicit, local, central?
    if message.type == 'report':
        return [('server', 'namlat.modules.report')]
    # other filtering rules:

    # else: forward to master or not?
    return []


def get_mail(module_, keep=False, type_=None):
    mails = dict()
    inbox = context.localdb['inbox']
    if module_ in inbox:
        mails = {k: inbox[module_][k]
                 for k in inbox[module_]
                 if type_ is None or inbox[module_][k].type == type_}
        if not keep:
            with context.localdb:
                for k in mails:
                    del inbox[module_][k]
    logger.debug("get_mail for module:%s returned %d mails.", module_, len(mails))
    return mails