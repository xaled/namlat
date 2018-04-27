import sys
import os
import jinja2
import time
import logging as _logging
from flask import render_template
from namlat.context import context
from namlat.utils.data import deep_copy
from namlat.utils.flask import FlaskRulesContainer
from namlat.modules import AbstractNamlatJob, get_mail
import namlat.utils.mail


script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(script_path))
# print(jinja_env.get_template("test.tpl").render(name="xaled"))
MAIL_TEMPLATE = 'templates/mail_report.tpl'
flask_rule_container = FlaskRulesContainer()
logger = _logging.getLogger(__name__)
with context.localdb:
    if 'modules' not in context.localdb:
        context.localdb['modules'] = dict()
    if __name__ not in context.localdb['modules']:
        context.localdb['modules'][__name__] = {'archive': {}, 'handlers_stack': {}}
module_db = context.localdb['modules'][__name__]
handlers_stack = module_db['handlers_stack']
archive = module_db['archive']


class ReportJob(AbstractNamlatJob):
    def init_job(self):
        pass

    def execute(self):
        logger.info("executing ReportJob")
        process_new_entries()
        executed_handlers = []
        for handler in self.get_report_handlers():
            if time.time() > handler.last_execute() + handler.period and handler.has_entries():
                logger.debug("making and sending report for handler=%s", handler.handler_id)
                handler.parse_entries()
                handler.make_report()
                handler.send()
                executed_handlers.append(handler.handler_id)
                handler.handler_executed()
        logger.debug("%d handlers executed", len(executed_handlers))
        if len(executed_handlers) > 0:
            self.send_report_entry("%d handlers executed" % len(executed_handlers), str(executed_handlers))
        # save changes
        context.localdb.save()

    def get_report_handlers(self):
        handlers = list()
        handlers.append(MailHandler(self.kwargs, 0, 'instant'))
        handlers.append(MailHandler(self.kwargs, 86400, 'daily'))
        handlers.append(MailHandler(self.kwargs, 604800, 'weekly'))
        handlers.append(MailHandler(self.kwargs, 2592000, 'monthly'))
        handlers.append(SmsHandler(self.kwargs, 0, 'instant'))
        handlers.append(SmsHandler(self.kwargs, 86400, 'daily'))
        handlers.append(SmsHandler(self.kwargs, 604800, 'weekly'))
        handlers.append(SmsHandler(self.kwargs, 2592000, 'monthly'))
        handlers.append(TelegramHandler(self.kwargs, 0, 'instant'))
        handlers.append(TelegramHandler(self.kwargs, 86400, 'daily'))
        handlers.append(TelegramHandler(self.kwargs, 604800, 'weekly'))
        handlers.append(TelegramHandler(self.kwargs, 2592000, 'monthly'))
        return handlers


class Handler:
    def __init__(self, jobargs, handler_class, period, period_name):
        self.handler_id = handler_class + "_" + period_name
        with context.localdb:
            if not self.handler_id in handlers_stack:
                handlers_stack[self.handler_id] = {'entries': {}, 'last_execute': 0.0}
        self.pointer = handlers_stack[self.handler_id]
        self.period = period
        self.period_name = period_name
        self.jobargs = jobargs
        self.reports = dict()

    def has_entries(self):
        return len(self.pointer['entries']) > 0

    def get_entries(self):
        return self.pointer['entries'].values()

    def last_execute(self):
        return self.pointer['last_execute']

    def handler_executed(self):
        with context.localdb:
            self.pointer['last_execute'] = time.time()
            self.pointer['entries'].clear()

    def parse_entries(self):
        self.reports = dict()
        for entry in self.get_entries():
            # entry keys: ['node_name', 'uri', 'entry_id', 'report_type', 'report_title', 'module_',
            # 'handlers', 'report_subtitle', 'title', 'message_body']
            # if entry['uri'] not in self.reports:
            report_key = "/%s/%s/%s/%s" % (entry['node_name'], entry['module_'], entry['report_type'],
                                              entry['report_id'])
            if report_key not in self.reports:
                if entry['report_id'] is None:
                    report_uri = ""
                else:
                    report_uri = "/reports/%s/%s/%s/%s" % (entry['node_name'], entry['module_'],
                                                           entry['report_type'], entry['report_id'])
                self.reports[report_key] = Report(entry['report_title'], entry['report_subtitle'], report_uri) #nr.Report(entry['report_title'], entry['report_subtitle'], entry['uri'])

            self.reports[report_key].entries.append(ReportEntry(entry['title'], entry['message_body'],
                                                                  entry['entry_id'], entry['actions']))


class MailHandler(Handler):
    def __init__(self, jobargs, period, period_name):
        super().__init__(jobargs, "mail", period, period_name)

    def make_report(self):
        self.subject = self.period_name + " namlat reports " + time.strftime("%d %b %Y", time.gmtime(time.time()))
        self.mail_body = jinja_env.get_template(MAIL_TEMPLATE).render(reports=self.reports.values(), subject=self.subject,
                                                                      url=self.jobargs['server'])
        logger.debug("MailHandler - subject : %s", self.subject)
        logger.debug("MailHandler - mail_body : %s", self.mail_body)

    def send(self): # TODO:
        namlat.utils.mail.send_html(self.subject, self.mail_body, self.jobargs['recipient'],
                                     self.jobargs['gmail_username'], self.jobargs['gmail_password'])
        #pass


class SmsHandler(Handler):
    def __init__(self, jobargs, period, period_name):
        super().__init__(jobargs, "sms", period, period_name)

    def make_report(self):
        pass

    def send(self):
        pass


class TelegramHandler(Handler):
    def __init__(self, jobargs, period, period_name):
        super().__init__(jobargs, "telegram", period, period_name)

    def make_report(self):
        pass

    def send(self):
        pass


class Report:
    def __init__(self, report_title, report_subtitle, report_uri):
        self.report_title = report_title
        self.report_subtitle = report_subtitle
        self.report_uri = report_uri
        self.entries = list()


class ReportEntry:
    def __init__(self, title, message_body, entry_id, actions):
        self.title = title
        self.message_body = message_body
        self.entry_id = entry_id
        self.actions = actions


def process_new_entries():
    new_reports_entries_count = 0
    for k, message in get_mail(__name__, type_='report').items():
        for nrp in message.content:
            nrp_copy = deep_copy(nrp)
            with context.localdb:
                key = "/%s/%s/%s/%s#%s" % (nrp['node_name'], nrp['module_'], nrp['report_type'],
                                           nrp['report_id'], nrp['entry_id'])
                # archive
                archive[key] = nrp_copy

                # handler stack
                for handler in nrp['handlers']:
                        if handler not in handlers_stack:
                            handlers_stack[handler] = {'entries': {}, 'last_execute': 0.0}
                        handlers_stack[handler]['entries'][key] = nrp_copy # dict(nrp)

            # increment new reports count
            new_reports_entries_count += 1

    logger.debug("processed %d new reports entries", new_reports_entries_count)


def mail_hook():
    logger.debug("mail_hook()")
    process_new_entries()


def get_flask_rules():
    return flask_rule_container.rules


@flask_rule_container.route('/')
def view_reports_root():
    reports = list(archive.values())
    keys = list(reports[0].keys())
    return render_template("report/reports.html", keys=keys, reports=reports)


@flask_rule_container.route('/<node>/<modul>/<report_type>/<report_id>')
def view_reports_by_type_and_id(node, module, report_type, report_id):
    return node + module + report_type + report_id

