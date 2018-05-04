import uuid
import logging as _logging
from namlat.context import context
from namlat.updates.messages import Message
from xaled_utils.json_serialize import JsonSerializable
import time

logger = _logging.getLogger(__name__)
NO_HANDLERS = []
DEFAULT_HANDLERS = ["mail_daily"]
DAILY_MAIL_HANDLERS = ["mail_daily"]
WEEKLY_MAIL_HANDLERS = ["mail_weekly"]
MONTHLY_MAIL_HANDLERS = ["mail_monthly"]
NOTIFICATION_HANDLERS = ["telegram_instant", "mail_instant"]
ALERT_HANDLERS = ["sms_instant", "telegram_instant", "mail_instant"]


class Report(JsonSerializable):
    def __init__(self, module_, report_id, report_type, handlers, node_name=None, report_title=None,
                 report_subtitle="", report_append=False, report_archived=True):
        self.node_name = node_name or context.node_name
        self.module_ = module_

        # report
        self.report_timestamp = time.time()
        self.report_append_timestamp = self.report_timestamp
        self.report_type = report_type
        self.report_id = report_id # report_id = None for transient reports
        if report_title is None:
            self.report_title = "%s.%s report for namla %s" % (self.module_, self.report_type, self.node_name)
        else:
            self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.report_append = report_append
        self.report_archived = report_archived
        self.handlers = handlers
        self.report_entries = list()
        self.report_uri = None

    def append_report_entry(self, title, message_body, entry_id=None, actions=None):
        actions = actions or list()
        new_entry_dict = ReportEntry(title, message_body, entry_id, actions)
        self.report_entries.append(new_entry_dict)

    def send_report(self):
        if len(self.report_entries) == 0:
            return
        message = Message([self.node_name, self.module_], [], 'report', self)
        message.send()

    def send_report_entry(self, title, message_body, entry_id=None, actions=None):
        actions = actions or list()
        self.append_report_entry(title, message_body, entry_id=entry_id, actions=actions)
        self.send_report()


class ReportEntry(JsonSerializable):
    # def __init__(self, title, message_body, entry_id=None, actions=[]):
    def __init__(self, title, message_body, entry_id, actions):
        self.timestamp = time.time()
        self.title = title
        self.message_body = message_body
        if entry_id is None:
            self.entry_id = uuid.uuid4().hex
        else:
            self.entry_id = entry_id
        self.actions = actions
        self.entry_uri = None


# # class NewReportMaker:
# class ReportMaker:
#     def __init__(self, module_, report_id, report_type, handlers, node_name=context.node_name,
#                  reporter_node='reporter', report_title=None, report_subtitle="", report_append=False):
#         # nodes and module
#         # self.inboxpointer = inboxpointer
#         self.node_name = node_name
#         self.reporter_node = reporter_node
#         self.module_ = module_
#
#         # report
#         self.report_timestamp = time.time()
#         self.report_type = report_type
#         self.report_id = report_id # report_id = None for transient reports
#         if report_title is None:
#             self.report_title = "%s.%s report for namla %s" % (self.module_, self.report_type, self.node_name)
#         else:
#             self.report_title = report_title
#         self.report_subtitle = report_subtitle
#         self.report_append = report_append
#         self.handlers = handlers
#         self.report_entries = list()
#
#     # def make_new_report_entry(self, title, message_body, entry_id=None, actions=[]):
#     #     return NewReportEntry(self.node_name, self.reporter_node, self.module_, self.report_type,
#     #                           self.report_id, self.report_title, self.report_subtitle, self.handlers,
#     #                           title, message_body, entry_id, actions)
#     #
#     def append_report_entry(self, title, message_body, entry_id=None, actions=None):
#         actions = actions or list()
#         new_entry_dict = ReportEntry(title, message_body, entry_id, actions).get_dict()
#         self.report_entries.append(new_entry_dict)
#
#     def send_report(self):
#         if len(self.report_entries) == 0:
#             return
#         message = Message([self.node_name, self.module_], [], 'report',
#                           list(self.report_entries))  # [[self.reporter_node, 'namlat.modules.report_job']]
#         message.send()
#         self.report_entries.clear()
#
#     def send_report_entry(self, title, message_body, entry_id=None, actions=None):
#         actions = actions or list()
#         self. append_report_entry(title, message_body, entry_id=entry_id, actions=actions)
#         self.send_report()
#


# class LogEntry:
#     def __init__(self, level, message, time_, module_):
#         self.level = level
#         self.message = message
#         self.time_ = time_
#         self.module_ = module_


# def append_new_report_entry(data_pointer, node_name, new_report_entry, reporter_node='reporter'):
#     # data_pointer['new_reports'][node_name].append(new_report_entry.get_dict())
#     data_pointer['inbox'][reporter_node].append(new_report_entry.get_dict())


