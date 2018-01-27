import namlat.report as nr
import namlat.updates as nu
from namlat.modules import AbstractNamlatJob
import namlat.utils.mail
import time
import logging as _logging
import sys, os
import jinja2

script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(script_path))
# print(jinja_env.get_template("test.tpl").render(name="xaled"))
MAIL_TEMPLATE = 'templates/mail_report.tpl'

logger = _logging.getLogger(__name__)


class ReportJob(AbstractNamlatJob):
    def init_job(self):
        pass

    def execute(self):
        logger.info("executing ReportJob")
        self.process_new_entries()
        executed_handlers = []
        for handler in self.get_report_handlers():
            if time.time() > handler.last_execute() + handler.period and handler.has_entries():
                logger.debug("making and sending report for handler=%s", handler.handler_id)
                handler.make_report()
                handler.send()
                executed_handlers.append(handler.handler_id)
                handler.handler_executed()
        logger.debug("%d handlers executed", len(executed_handlers))
        if len(executed_handlers) > 0:
            self.report("%d handlers executed" % len(executed_handlers), str(executed_handlers))

    def process_new_entries(self):
        for ad in self.data['new_reports']:
            for nrp in self.data['new_reports'][ad]:
                # report archive
                report_archive = self.data['reports']['archive']
                if not ad in report_archive:
                    report_archive[ad] = dict()
                if not nrp['report_module'] in report_archive:
                    report_archive[ad][nrp['report_module']] = dict()
                if not nrp['report_type'] in report_archive[ad][nrp['report_module']]:
                    report_archive[ad][nrp['report_module']][nrp['report_type']] = dict()
                    report_object_pointer = report_archive[ad][nrp['report_module']][nrp['report_type']]
                    report_object_pointer['title'] = nrp['report_title']
                    report_object_pointer['subtitle'] = nrp['report_subtitle']
                    report_object_pointer['uri'] = "/reports/%s/%s/%s" % (ad, nrp['report_module'], nrp['report_type'])
                    report_object_pointer['entries'] = dict()
                    report_object_pointer = report_archive[ad][nrp['report_module']][nrp['report_type']]
                report_object_pointer['entries'][nrp['entry_id']] = nr.make_report_entry(nrp['entry_id'], nrp['title'],
                                                                                         nrp['message_body'])

                # handlers stack
                handlers_stack = self.data['reports']['handlers_stack']
                for handler in nrp['handlers']:
                    if not handler in handlers_stack:
                        handlers_stack[handler] = dict()
                    key = report_object_pointer['uri'] + "#" + nrp['entry_id']
                    handlers_stack[handler][key] = dict(nrp)
                    handlers_stack[handler][key]['uri'] = report_object_pointer['uri']
                    handlers_stack[handler][key]['address'] = ad

    def get_report_handlers(self):
        handlers = list()
        handlers.append(MailHandler(self.kwargs, self.data, 0, 'instant'))
        handlers.append(MailHandler(self.kwargs, self.data, 86400, 'daily'))
        handlers.append(MailHandler(self.kwargs, self.data, 604800, 'weekly'))
        handlers.append(MailHandler(self.kwargs, self.data, 2592000, 'monthly'))
        return handlers


def periodic_handler():
    def send():
        pass

    send()


class Handler:
    def __init__(self, jobargs, datapointer, handler_class, period, period_name):
        self.handler_id = handler_class + "_" + period_name
        self.pointer = datapointer['reports']['handlers_stack'][self.handler_id]
        self.data = datapointer
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
        self.pointer['last_execute'] = time.time()
        for entry in self.pointer['entries'].values():
            try:
                report_object_pointer = self.data['reports']['archive'][entry['address']][entry['report_module']][
                    entry['report_type']]
                if 'report_id' not in report_object_pointer:
                    report_object_pointer['report_id'] = entry['report_id']
            except Exception as e:
                logger.error("error while updating report_id: " + str(e), exc_info=True)
        self.pointer['entries'].clear()

    def parse_entries(self):
        self.reports = dict()
        for entry in self.get_entries():
            # entry keys: ['address', 'uri', 'entry_id', 'report_type', 'report_title', 'report_module',
            # 'handlers', 'report_subtitle', 'title', 'message_body']
            if entry['uri'] not in self.reports:
                # if report_title is None #  TODO:
                self.reports[entry['uri']] = nr.Report(entry['report_title'], entry['report_subtitle'], entry['uri'])
            self.reports[entry['uri']].entries.append(nr.ReportEntry(entry['title'], entry['message_body'],
                                                                     entry['entry_id']))


class MailHandler(Handler):
    def __init__(self, jobargs, datapointer, period, period_name):
        super().__init__(jobargs, datapointer, "mail", period, period_name)

    def make_report(self):
        self.subject = self.period_name + " namlat reports " + time.strftime("%d %b %Y", time.gmtime(time.time()))
        self.mail_body = jinja_env.get_template(MAIL_TEMPLATE).render(reports=self.reports, subject=self.subject,
                                                                      url="http://server/")

    def send(self):
        namlat.utils.mail.send_html(self.subject, self.mail_body, self.jobargs['recipient'],
                                    self.jobargs['gmail_username'], self.jobargs['gmail_password'])


class SmsHandler(Handler):
    def __init__(self, jobargs, datapointer, period, period_name):
        super().__init__(jobargs, datapointer, "sms", period, period_name)

    def make_report(self):
        pass

    def send(self):
        pass


class TelegramHandler(Handler):
    def __init__(self, jobargs, datapointer, period, period_name):
        super().__init__(jobargs, datapointer, "telegram", period, period_name)

    def make_report(self):
        pass

    def send(self):
        pass
