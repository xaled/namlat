import logging as _logging

logger = _logging.getLogger(__name__)
context = None


class Report:
    """ type_: sms, mail, telegram
        period:
        uri:

    """
    def __init__(self, module_, uri, type_, period, entries, title="{PERIODLY} report of {MODULE}", subtitle=""):
        self.module = module_
        self.uri = uri
        self.type = type_
        self.period = period
        self.title = title
        self.subtitle = subtitle
        self.entries = list()
        for entry in entries:
            self.entries.append(entry)


class ReportEntry:
    def __init__(self, title, message_body, anchor, entry_id=None):
        self.title = title
        self.message_body = message_body
        self.anchor = anchor
        self.id = entry_id


class NewReportEntry:
    def __init__(self, title, message_body, module_, report_id, report_title=None,
                 report_subtitle="", handlers=[], entry_id=None):
        self.title = title
        self.message_body = message_body
        self.report_id = report_id
        self.entry_id = entry_id
        self.module_ = module_
        self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.handlers = handlers


class NewReportMaker:
    def __init__(self, module_, report_id, report_title=None, report_subtitle="", handlers=[]):
        self.report_id = report_id
        self.module_ = module_
        self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.handlers = handlers

    def make_new_report_entry(self, title, message_body, entry_id=None):
        return NewReportEntry(title, message_body, self.module_, self.report_id, self.report_title,
                              self.report_subtitle, self.handlers, entry_id)

class LogEntry:
    def __init__(self, level, message, time_, module_):
        self.level = level
        self.message = message
        self.time_ = time_
        self.module_ = module_





def report(report_):  # TODO should return edits instead
    _import_context()
    context.data['new_reports'][context.address].append(report_.__dict__)



