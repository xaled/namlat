import logging as _logging

logger = _logging.getLogger(__name__)
context = None


class Report:
    def __init__(self, module_, uri, type_, period, entries, title="{PERIODLY} report of {MODULE}", subtitle=""):
        self.__dict__ = dict()
        self.__dict__['module'] = module_
        self.__dict__['uri'] = uri
        self.__dict__['type'] = type_
        self.__dict__['period'] = period
        self.__dict__['title'] = title
        self.__dict__['subtitle'] = subtitle
        self.__dict__['entries'] = list()
        for entry in entries:
            self.__dict__['entries'].append(entry.__dict__)


class Entry:
    def __init__(self, title, message_body, anchor, id_=None):
        self.__dict__ = dict()
        self.__dict__['title'] = title
        self.__dict__['message_body'] = message_body
        self.__dict__['anchor'] = anchor
        self.__dict__['id'] = id_


def _import_context():
    global context
    if context is None:
        from namlat import context


def report(report_):
    _import_context()
    context.data['new_reports'][context.address].append(report_.__dict__)
