import uuid
import logging as _logging

logger = _logging.getLogger(__name__)
context = None
NEW_REPORT_ENTRY_KEYS = ['entry_id', 'report_type', 'report_title', 'report_module', 'handlers',
                         'report_subtitle', 'title', 'message_body']
NO_HANDLERS = []
DEFAULT_HANDLERS = ["mail_daily"]
DAILY_MAIL_HANDLERS = ["mail_daily"]
WEEKLY_MAIL_HANDLERS = ["mail_weekly", "telegram_weekly"]
MONTHLY_MAIL_HANDLERS = ["mail_monthly", "telegram_monthly"]
NOTIFICATION_HANDLERS = ["telegram_instant", "mail_instant"]
WARNING_HANDLERS = ["telegram_instant", "mail_instant"]
ALERT_HANDLERS = ["sms_instant", "telegram_instant", "mail_instant"]


class Report:
    """ type_: sms, mail, telegram
        period:
        uri:

    """
    def __init__(self, report_title, report_subtitle, report_uri):
        # omited params: address, report_module, report_type
        # title="{PERIODLY} report of {MODULE}",
        self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.report_uri = report_uri
        self.report_id = uuid.uuid4().hex
        self.entries = list()


class ReportEntry:
    def __init__(self, title, message_body, entry_id):
        self.title = title
        self.message_body = message_body
        self.entry_id = entry_id


def make_report_entry(entry_id, title, message_body):
    report_entry = dict()
    report_entry['entry_id'] = entry_id
    report_entry['title'] = title
    report_entry['message_body'] = message_body
    return report_entry


class NewReportEntry:
    def __init__(self, title, message_body, report_module, report_type, report_title=None,
                 report_subtitle="", handlers=DEFAULT_HANDLERS, entry_id=None):
        self.title = title
        self.message_body = message_body
        self.report_type = report_type
        #self.report_id = report_id
        if entry_id is None:
            self.entry_id = uuid.uuid4().hex
        else:
            self.entry_id = entry_id
        self.report_module = report_module
        self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.handlers = handlers

    def get_dict(self):
        ret = dict()
        for k in NEW_REPORT_ENTRY_KEYS:
            ret[k] = self.__dict__[k]
        return ret


class NewReportMaker:
    def __init__(self, module_, report_type, report_title=None, report_subtitle="", handlers=[]):
        self.report_type = report_type
        self.module_ = module_
        self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.handlers = handlers

    def make_new_report_entry(self, title, message_body, entry_id=None):
        return NewReportEntry(title, message_body, self.module_, self.report_type, self.report_title,
                              self.report_subtitle, self.handlers, entry_id)




class LogEntry:
    def __init__(self, level, message, time_, module_):
        self.level = level
        self.message = message
        self.time_ = time_
        self.module_ = module_


def append_new_report_entry(data_pointer, address, new_report_entry):
    data_pointer['new_reports'][address].append(new_report_entry.get_dict())


