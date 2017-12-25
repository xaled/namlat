import time
import logging as _logging
import namlat.report as nr
import namlat.updates as nu


logger = _logging.getLogger(__name__)


def execute():
    _import_context()
    update_new_entries()
    executed_handlers = []
    edits = []
    for handler in get_report_handlers():
        if time.time() > handler.last_execute() + handler.period and handler.has_entries():
            handler.make_report()
            handler.send()
            executed_handlers.append(handler.handler_id)
            handler.last_execute()
    if len(executed_handlers) > 0:
        nr.report(nu.Update(edits))
    return nu.Update()  # TODO: