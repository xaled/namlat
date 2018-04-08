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
        self.default_report_maker = nr.NewReportMaker(self.module_,'_', '_', nr.NOTIFICATION_HANDLERS,
                                                      report_title="Default Report for module %s, namla: %s" %
                                                                   (self.module_, self.context.node_name))

    def get_update(self):
        return nu.Update(self.data.edits)

    def init_job(self):
        pass

    def execute(self):
        pass

    def append_report_entry(self, title, message_body, entry_id=None, actions=[]):
        self.default_report_maker.append_report_entry(title, message_body, entry_id, actions)

    def send_report_entry(self, title, message_body, entry_id=None, actions=[]):
        self.default_report_maker.send_report_entry(title, message_body, entry_id, actions)

    def send_report(self):
        self.default_report_maker.send_report()

    def get_report_maker(self, report_id, report_type, handlers,
                 reporter_node='reporter', report_title=None, report_subtitle="", report_archived=True):
        return nr.NewReportMaker(self.module_, report_id, report_type, handlers,
                                 node_name=context.node_name, reporter_node=reporter_node, report_title=report_title,
                                 report_subtitle=report_subtitle, report_archived=report_archived)

    def finished(self):
        pass

    def get_mail(self, keep=False, type_=None):
        mails = dict()

        if self.module_ in context.localdb['inbox']:
            if type_ is None:
                mails = dict(context.localdb['inbox'])
            else:
                for k in context.localdb['inbox'][self.module_]:
                    if context.localdb['inbox'][self.module_][k].type == type_:
                        mails[k] = context.localdb['inbox'][k]
            if not keep:
                with context.localdb:
                    for m in mails:
                        context.localdb.remove(m)
        logger.debug("get_mail for module:%s returned %d mails.", self.module_, len(mails))
        return mails
