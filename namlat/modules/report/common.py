import os
import time
import logging as _logging
from namlat.context import context
from namlat.modules import get_mail
import uuid
from xaled_utils.json_min_db import JsonMinConnexion
logger = _logging.getLogger(__name__)
with context.localdb:
    if 'modules' not in context.localdb:
        context.localdb['modules'] = dict()
    if __name__ not in context.localdb['modules']:
        context.localdb['modules'][__name__] = {'archive': {}, 'handlers_stack': {}}
module_db = context.localdb['modules'][__name__]
handlers_stack = module_db['handlers_stack']
archive = module_db['archive']


def process_new_entries():
    new_reports_entries_count = 0
    for k, message in get_mail("namlat.modules.report", type_='report').items():
        report = message.content
        # updating uris
        report.report_uri = "/%s/%s/%s/%s" % (report.node_name, report.module_, report.report_type, report.report_id)
        for entry in report.report_entries:
            entry.entry_uri = "%s#%s" % (report.report_uri, entry.entry_id)

        with context.localdb:
            # archive
            if report.report_archived:
                if report.report_uri not in archive:
                    archive[report.report_uri] = uuid.uuid3(uuid.NAMESPACE_URL, report.report_uri).hex + ".json"

                report_db = get_report_db(report.report_uri)
                with report_db:
                    if report.report_append or 'report' not in report_db:
                        report_db['report'] = report
                    else:
                        report_db['report'].report_entries.extend(report.report_entries)
                        report_db['report'].report_append_timestamp = time.time()

            # handler stack
            for handler in report.handlers:
                if handler not in handlers_stack:
                    handlers_stack[handler] = {'reports': [], 'last_execute': 0.0}
                if len(report.report_entries) > 0:
                    handlers_stack[handler]['reports'].append(report)

        # increment new reports count
        new_reports_entries_count += len(report.report_entries)

    logger.debug("processed %d new reports entries", new_reports_entries_count)


def get_report_db(report_uri):
    return JsonMinConnexion(os.path.join(context.data_dir, archive[report_uri]), indent=None)