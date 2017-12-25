import namlat.updates as nu
from namlat.utils.edits_dict import EditDict
import logging

logger = logging.getLogger(__name__)


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

    def get_update(self):
        return nu.Update(self.data.edits)

    def init_job(self):
        pass

    def execute(self):
        pass