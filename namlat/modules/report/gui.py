import logging as _logging
from flask import render_template
from namlat.utils.flask import FlaskRulesContainer

logger = _logging.getLogger(__name__)
flask_rule_container = FlaskRulesContainer()


@flask_rule_container.route('/')
def view_reports_root():
    from namlat.modules.report.common import archive
    reports = archive.keys()
    return render_template("report/list_reports.html", reports=reports, title="Report listing",
                           )


@flask_rule_container.route('/<node_name>/<modul>/<report_type>/<report_id>')
def view_reports_by_type_and_id(node_name, modul, report_type, report_id):
    from namlat.modules.report.common import get_report_db
    report_uri = "/%s/%s/%s/%s" % (node_name, modul, report_type, report_id)

    report_db = get_report_db(report_uri)
    report = report_db['report']
    return render_template("report/reports.html", report=report, title="Report View",
                           keys=report.report_entries[0].__dict__.keys(), section_title=report.report_title)
