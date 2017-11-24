import time
import logging as _logging
import namlat_report as nr
import namlat_updates as nu


logger = _logging.getLogger(__name__)
context = None


def execute():
    _import_context()
    update_new_entries()
    executed_handlers = []
    edits = []
    for handler in get_report_handlers():
        if time.time() > handler.last_execute() + handler.period and handler.has_entries():
            handler.make_report()
            handler.send()
            executed_handlers.append(handler.handler_id)
            handler.last_execute()
    if len(executed_handlers) > 0:
        nr.report(nu.Update(edits))
    return nu.Update()  # TODO:


def _import_context():
    global context
    if context is None:
        from namlat import context


def update_new_entries():
    pass
    # for each report in new_reports stack
    # dispatch report to handlers stack


def get_report_handlers():
    return []


def periodic_handler():
    def send():
        pass
    send()


class Handler:
    def __init__(self, handler_class, period, period_name):
        self.handler_id = handler_class + "_" + period_name
        self._pointer = context.data['reports'][self.handler_id]
        self.period = period
        self.period_name = period_name

    def has_entries(self):
        return len(self._pointer['entries']) > 0

    def get_entries(self):
        return self._pointer['entries'].values()

    def last_execute(self):
        return self._pointer['last_execute']

    def handler_executed(self):
        pass
        # empty entries edits
        # last_execute=time.time() edit
        # return edits?


class MailHandler(Handler):
    def __init__(self, period, period_name):
        super().__init__("mail" , period, period_name)

    def make_report(self):
        pass

    def send(self):
        pass


class SmsHandler(Handler):
    def __init__(self, period, period_name):
        super().__init__("sms", period, period_name)

    def make_report(self):
        pass

    def send(self):
        pass


class TelegramHandler(Handler):
    def __init__(self, period, period_name):
        super().__init__("telegram", period, period_name)

    def make_report(self):
        pass

    def send(self):
        pass