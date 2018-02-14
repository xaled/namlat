import namlat.updates as nu
import namlat.report as nr
from namlat.utils.edits_dict import EditDict
from namlat.context import context
import logging

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
        self.data = EditDict(self.context.data)
        self.module_ = module_
        self.class_ = class_
        # self.default_report_maker = nr.NewReportMaker(module_, "_")
        self.default_report_maker = nr.NewReportMaker(self.data['inbox'], self.module_, '_', nr.NOTIFICATION_HANDLERS,
                                                      report_title="Default Report for module %s, namla: %s" %
                                                                   (self.module_, self.context.node_name))

    def get_update(self):
        return nu.Update(self.data.edits)

    def init_job(self):
        pass

    def execute(self):
        pass

    def report(self, title, message_body, entry_id=None, report_maker=None, actions=[]):
        if report_maker is None:
            report_maker = self.default_report_maker
        # new_report_entry = report_maker.make_new_report_entry(title, message_body, entry_id)
        # nr.append_new_report_entry(self.data, self.context.node_name, new_report_entry)
        report_maker.append_new_report_entry(title, message_body, entry_id, actions)

    def get_report_maker(self, report_type, handlers, report_id=None,
                 reporter_node='reporter', report_title=None, report_subtitle=""):
        return nr.NewReportMaker(self.data['inbox'], self.module_, report_type, handlers, report_id=report_id,
                                 node_name=context.node_name, reporter_node=reporter_node, report_title=report_title,
                                 report_subtitle=report_subtitle)

    def finished(self):
        pass