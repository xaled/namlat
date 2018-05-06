import namlat.updates as nu
import namlat.report as nr
from namlat.utils.edits_dict import EditDict
from namlat.utils.flask import FlaskRulesContainer
from namlat.context import context
from namlat.updates.message_server import get_mail
import logging
import importlib

logger = logging.getLogger(__name__)


# context = None


# def _import_context():
#     global context
#     if context is None:
#         from namlat import context
#     return context


class AbstractNamlatJob:
    def __init__(self, module_, class_):
        self.context = context
        self.kwargs = dict()
        # self.data = EditDict(self.context.data)
        self.module_ = module_
        self.class_ = class_
        # self.default_report = nr.NewReportMaker(module_, "_")
        self.default_report = nr.Report(self.module_, 'default', 'default', nr.WEEKLY_MAIL_HANDLERS,
                                        report_title="Default Report for module %s, namla: %s" %
                                                     (self.module_, self.context.node_name))

    def get_update(self):
        # return nu.Update(self.data.edits)
        return None

    def init_job(self):
        pass

    def execute(self):
        pass

    def append_report_entry(self, title, message_body, entry_id=None, actions=None):
        actions = actions or list()
        self.default_report.append_report_entry(title, message_body, entry_id, actions)

    def send_report_entry(self, title, message_body, entry_id=None, actions=None):
        actions = actions or list()
        self.default_report.send_report_entry(title, message_body, entry_id, actions)

    def send_report(self):
        self.default_report.send_report()

    def get_report(self, report_id, report_type, handlers, report_title=None, report_subtitle="",
                   report_append=False, report_archived=True):
        return nr.Report(self.module_, report_id, report_type, handlers,
                         node_name=context.node_name, report_title=report_title,
                         report_subtitle=report_subtitle, report_append=report_append, report_archived=report_archived)

    def finished(self):
        pass

    def get_mail(self, keep=False, type_=None):
        return get_mail(self.module_, keep=keep, type_=type_)


def get_module_route_rules(module_name, **kwargs):
    module_ = importlib.import_module(module_name)

    # get_flask_rules function
    if 'get_flask_rules' in module_.__dict__ and callable(module_.__dict__['get_flask_rules']):
        logger.debug("calling get_flask_rules from module: %s." % module_name)
        return module_.__dict__['get_flask_rules'](**kwargs)

    # flask_rule_container instance
    if 'flask_rule_container' in module_.__dict__ \
            and isinstance(module_.__dict__['rule_container'], FlaskRulesContainer):
        logger.debug("getting  flask_rule_container from module: %s." % module_name)
        return module_.__dict__['rule_container'].rules
