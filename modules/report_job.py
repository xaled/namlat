import time
import logging
import namlat_report as nr
import namlat_updates as nu
logger = logging.getLogger(__name__)

def execute(data_pointer):
    global data
    data = data_pointer
    update_new_entries()
    executed_handlers = []
    for handler in get_report_handlers():
        if time.time() > handler['last_execute'] + handler['period'] and handler.has_entries():
            handler.make_report()
            handler.send()
            executed_handlers.append(handler['name'])
            #TODO update last_execute and period
    if len(executed_handlers) > 0:
        nr.report()  # TODO:
    return nu.Update()  # TODO:



def update_new_entries():
    pass

def get_report_handlers():
    return []