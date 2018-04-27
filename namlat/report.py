import uuid
import logging as _logging
from namlat.context import context
from namlat.updates.messages import Message

logger = _logging.getLogger(__name__)
# context = None
# NEW_REPORT_ENTRY_KEYS = ['entry_id', 'report_type', 'report_title', 'report_module', 'handlers',
#                          'report_subtitle', 'title', 'message_body']
NO_HANDLERS = []
DEFAULT_HANDLERS = ["mail_daily"]
DAILY_MAIL_HANDLERS = ["mail_daily"]
WEEKLY_MAIL_HANDLERS = ["mail_weekly", "telegram_weekly"]
MONTHLY_MAIL_HANDLERS = ["mail_monthly", "telegram_monthly"]
NOTIFICATION_HANDLERS = ["telegram_instant", "mail_instant"]
WARNING_HANDLERS = ["telegram_instant", "mail_instant"]
ALERT_HANDLERS = ["sms_instant", "telegram_instant", "mail_instant"]


# class Report:
#     """ type_: sms, mail, telegram
#         period:
#         uri:
#
#     """
#     def __init__(self, report_title, report_subtitle, report_uri, report_id): # report_id==None for transient reports
#         # omited params: address, report_module, report_type
#         # title="{PERIODLY} report of {MODULE}",
#         self.report_title = report_title
#         self.report_subtitle = report_subtitle
#         self.report_uri = report_uri
#         # self.report_id = uuid.uuid4().hex
#         self.report_id = report_id
#         self.entries = list()
#
#
# class ReportEntry:
#     def __init__(self, title, message_body, entry_id):
#         self.title = title
#         self.message_body = message_body
#         self.entry_id = entry_id


# def make_report_entry(entry_id, title, message_body):
#     report_entry = dict()
#     report_entry['entry_id'] = entry_id
#     report_entry['title'] = title
#     report_entry['message_body'] = message_body
#     return report_entry


class NewReportEntry:
    # def __init__(self, title, message_body, entry_id=None, actions=[]):
    def __init__(self, node_name, module_, report_type, report_id, report_title, report_subtitle, report_archived,
                 handlers, title, message_body, entry_id, actions):
        # nodes and module
        self.node_name =node_name
        # self.reporter_node = reporter_node
        self.module_ = module_

        # report
        self.report_type = report_type
        self.report_id = report_id # report_id = None for transient reports
        self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.report_archived = report_archived
        self.handlers = handlers

        # entry
        self.title = title
        self.message_body = message_body
        if entry_id is None:
            self.entry_id = uuid.uuid4().hex
        else:
            self.entry_id = entry_id
        self.actions = actions

        # self.title = title
        # self.message_body = message_body
        # self.report_type = report_type
        # #self.report_id = report_id
        # # if entry_id is None:
        # #     self.entry_id = uuid.uuid4().hex
        # # else:
        # self.entry_id = entry_id
        # self.report_module = report_module
        # self.report_title = report_title
        # self.report_subtitle = report_subtitle
        # self.handlers = handlers

    def get_dict(self):
        return dict(self.__dict__)
        # ret = dict()
        # for k in NEW_REPORT_ENTRY_KEYS:
        #     ret[k] = self.__dict__[k]
        # return ret


class NewReportMaker:
    def __init__(self, module_, report_id, report_type, handlers, node_name=context.node_name,
                 reporter_node='reporter', report_title=None, report_subtitle="", report_archived=True):
        # nodes and module
        # self.inboxpointer = inboxpointer
        self.node_name =node_name
        self.reporter_node = reporter_node
        self.module_ = module_

        # report
        self.report_type = report_type
        self.report_id = report_id # report_id = None for transient reports
        if report_title is None:
            self.report_title = "%s.%s report for namla %s" % (self.module_, self.report_type, self.node_name)
        else:
            self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.report_archived = report_archived
        self.handlers = handlers
        self.report_entries = list()

    # def make_new_report_entry(self, title, message_body, entry_id=None, actions=[]):
    #     return NewReportEntry(self.node_name, self.reporter_node, self.module_, self.report_type,
    #                           self.report_id, self.report_title, self.report_subtitle, self.handlers,
    #                           title, message_body, entry_id, actions)
    #
    def append_report_entry(self, title, message_body, entry_id=None, actions=None):
        actions = actions or list()
        new_entry_dict = NewReportEntry(self.node_name, self.module_, self.report_type, self.report_id,
                                        self.report_title, self.report_subtitle, self.report_archived, self.handlers,
                                        title, message_body, entry_id, actions).get_dict()
        self.report_entries.append(new_entry_dict)

    def send_report_entry(self, title, message_body, entry_id=None, actions=None):
        actions = actions or list()
        new_entry_dict = NewReportEntry(self.node_name, self.module_, self.report_type, self.report_id,
                                        self.report_title, self.report_subtitle, self.report_archived, self.handlers,
                                        title, message_body, entry_id, actions).get_dict()
        message = Message([self.node_name, self.module_], [], 'report',
                          [new_entry_dict])  # [[self.reporter_node, 'namlat.modules.report_job']]
        message.send()

    def send_report(self):
        if len(self.report_entries) == 0:
            return
        message = Message([self.node_name, self.module_], [], 'report',
                          list(self.report_entries))  # [[self.reporter_node, 'namlat.modules.report_job']]
        message.send()
        self.report_entries.clear()






# class LogEntry:
#     def __init__(self, level, message, time_, module_):
#         self.level = level
#         self.message = message
#         self.time_ = time_
#         self.module_ = module_


# def append_new_report_entry(data_pointer, node_name, new_report_entry, reporter_node='reporter'):
#     # data_pointer['new_reports'][node_name].append(new_report_entry.get_dict())
#     data_pointer['inbox'][reporter_node].append(new_report_entry.get_dict())


