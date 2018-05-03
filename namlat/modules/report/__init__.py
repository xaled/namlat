from namlat.modules.report.common import process_new_entries
from namlat.modules.report.jobs import ReportJob
from namlat.modules.report.gui import flask_rule_container
import logging as _logging
logger = _logging.getLogger(__name__)


def mail_hook():
    logger.debug("mail_hook()")
    process_new_entries()


def get_flask_rules():
    return flask_rule_container.rules