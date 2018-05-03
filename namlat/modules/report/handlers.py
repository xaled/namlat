import jinja2
import time
import logging as _logging
from namlat.context import context
from namlat.config import JINJA2_TEMPLATE_DIR
import namlat.utils.mail

logger = _logging.getLogger(__name__)
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(JINJA2_TEMPLATE_DIR))


class Handler:
    def __init__(self, jobargs, handler_class, period, period_name):
        from namlat.modules.report.common import handlers_stack
        self.handler_id = handler_class + "_" + period_name
        with context.localdb:
            if self.handler_id not in handlers_stack:
                handlers_stack[self.handler_id] = {'reports': [], 'last_execute': 0.0}
        self.pointer = handlers_stack[self.handler_id]
        self.period = period
        self.period_name = period_name
        self.jobargs = jobargs
        # self.reports = dict()

    def has_entries(self):
        return len(self.pointer['reports']) > 0

    def get_reports(self):
        return self.pointer['reports']

    def last_execute(self):
        return self.pointer['last_execute']

    def handler_executed(self):
        with context.localdb:
            self.pointer['last_execute'] = time.time()
            self.pointer['reports'].clear()


class MailHandler(Handler):
    def __init__(self, jobargs, period, period_name):
        self.subject = ""
        self.mail_body = ""
        super().__init__(jobargs, "mail", period, period_name)

    def make_report(self):
        self.subject = self.period_name + " namlat reports " + time.strftime("%d %b %Y", time.gmtime(time.time()))
        self.mail_body = jinja_env.get_template('mail_report.html').render(reports=self.get_reports(),
                                                                          subject=self.subject,
                                                                          url=self.jobargs['server'])
        logger.debug("MailHandler - subject : %s", self.subject)
        logger.debug("MailHandler - mail_body : %s", self.mail_body)

    def send(self):  # TODO:
        namlat.utils.mail.send_html(self.subject, self.mail_body, self.jobargs['recipient'],
                                    self.jobargs['gmail_username'], self.jobargs['gmail_password'])
        # pass


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
