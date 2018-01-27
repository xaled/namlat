import namlat.updates as nu
import namlat.report as nr
from namlat.utils.edits_dict import EditDict
import logging

logger = logging.getLogger(__name__)
context = None


def _import_context():
    global context
    if context is None:
        from namlat import context
    return context


class AbstractNamlatJob:
    def __init__(self, module_, class_):
        self.context = _import_context()
        self.kwargs = dict()
        self.data = EditDict(self.context.data)
        self.module_ = module_
        self.class_ = class_
        self.default_report_maker = nr.NewReportMaker(module_, "_")

    def get_update(self):
        return nu.Update(self.data.edits)

    def init_job(self):
        pass

    def execute(self):
        pass

    def report(self, title, message_body, entry_id=None, report_maker=None):
        if report_maker is None:
            report_maker = self.default_report_maker
        new_report_entry = report_maker.make_new_report_entry(title, message_body, entry_id)
        nr.append_new_report_entry(self.data, self.context.address, new_report_entry)

    def finished(self):
        pass