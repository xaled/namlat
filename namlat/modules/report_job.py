from namlat.context import context
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
                handler.parse_entries()
                handler.make_report()
                handler.send()
                executed_handlers.append(handler.handler_id)
                handler.handler_executed()
        logger.debug("%d handlers executed", len(executed_handlers))
        if len(executed_handlers) > 0:
            self.report("%d handlers executed" % len(executed_handlers), str(executed_handlers))
        # save changes
        context.localdb.save()

    def process_new_entries(self):
        new_reports_entries_count = 0
        to_remove = list()
        if 'reports' not in self.data:
            self.data['reports'] = {'archive':{} , 'handlers_stack':{}}
        # for ad in self.data['new_reports']:
        #     for nrp in self.data['new_reports'][ad]:
        for message in self.data['inbox'][context.node_name]:
            if message['to_module'] == self.module_ and message['type'] == 'report':
                to_remove.append(message)
                nrp = message['content']
                # report archive TODO: not for now
                # report_archive = self.data['reports']['archive']
                # if not ad in report_archive:
                #     report_archive[ad] = dict()
                # if not nrp['report_module'] in report_archive:
                #     report_archive[ad][nrp['report_module']] = dict()
                # if not nrp['report_type'] in report_archive[ad][nrp['report_module']]:
                #     report_archive[ad][nrp['report_module']][nrp['report_type']] = dict()
                #     report_object_pointer = report_archive[ad][nrp['report_module']][nrp['report_type']]
                #     report_object_pointer['title'] = nrp['report_title']
                #     report_object_pointer['subtitle'] = nrp['report_subtitle']
                #     report_object_pointer['uri'] = "/reports/%s/%s/%s" % (ad, nrp['report_module'], nrp['report_type'])
                #     report_object_pointer['entries'] = dict()
                #     report_object_pointer = report_archive[ad][nrp['report_module']][nrp['report_type']]
                # report_object_pointer['entries'][nrp['entry_id']] = nr.make_report_entry(nrp['entry_id'], nrp['title'],
                #                                                                          nrp['message_body'])

                # handlers stack
                if 'report_handlers_stack' not in  context.localdb:
                    context.localdb['report_handlers_stack'] = dict()
                handlers_stack = context.localdb['report_handlers_stack']

                for handler in nrp['handlers']:
                    if not handler in handlers_stack:
                        handlers_stack[handler] = {'entries': {}, 'last_execute':0.0}

                    #key = report_object_pointer['uri'] + "#" + nrp['entry_id']
                    # if nrp['report_id'] is None: # transient report:
                    #     # uri = ""
                    #     key = "/%s/%s/%s/%s#%s" %(nrp['node_name'], nrp['report_module'], nrp['report_type'],
                    #                               nrp['report_id'], nrp['entry_id'])
                    # else:
                    #     # uri =  "/reports/%s/%s/%s/%s" % (nrp['node_name'], nrp['report_module'], nrp['report_type'],
                    #     #                                  nrp['report_id'])
                    #     # uri = "/reports/%s" % nrp['report_id']
                    key = "/%s/%s/%s/%s#%s" %(nrp['node_name'], nrp['report_module'], nrp['report_type'],
                                                  'None', nrp['entry_id'])
                    handlers_stack[handler]['entries'][key] = nrp.deep_copy() # dict(nrp)
                    # handlers_stack[handler]['entries'][key]['uri'] = uri
                    # handlers_stack[handler]['entries'][key]['node_name'] = ad

                # increment new reports count
                new_reports_entries_count += 1



        # clear new reports
        for message in to_remove:
            self.data['inbox'][context.node_name].remove(message)


        logger.debug("processed %d new reports entries", new_reports_entries_count)

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
        if 'report_handlers_stack' not in context.localdb:
            context.localdb['report_handlers_stack'] = dict()
        handlers_stack = context.localdb['report_handlers_stack']
        if not self.handler_id in handlers_stack:
            context.localdb['report_handlers_stack'][self.handler_id] = {'entries': {}, 'last_execute': 0.0}
        self.pointer = context.localdb['report_handlers_stack'][self.handler_id]
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
        # for entry in self.pointer['entries'].values(): # TODO: not for now, continue archiving (Later)
        #     try:
        #         report_object_pointer = self.data['reports']['archive'][entry['node_name']][entry['report_module']][
        #             entry['report_type']]
        #         if 'report_id' not in report_object_pointer:
        #             report_object_pointer['report_id'] = entry['report_id']
        #     except Exception as e:
        #         logger.error("error while updating report_id: " + str(e), exc_info=True)
        self.pointer['entries'].clear()

    def parse_entries(self):
        self.reports = dict()
        for entry in self.get_entries():
            # entry keys: ['node_name', 'uri', 'entry_id', 'report_type', 'report_title', 'report_module',
            # 'handlers', 'report_subtitle', 'title', 'message_body']
            # if entry['uri'] not in self.reports:
            report_key = "/%s/%s/%s/%s" % (entry['node_name'], entry['report_module'], entry['report_type'],
                                              entry['report_id'])
            if report_key not in self.reports:
                if entry['report_id'] is None:
                    report_uri = ""
                else:
                    report_uri = "/reports/%s/%s/%s/%s" % (entry['node_name'], entry['report_module'],
                                                           entry['report_type'], entry['report_id'])
                self.reports[report_key] = Report(entry['report_title'], entry['report_subtitle'], report_uri) #nr.Report(entry['report_title'], entry['report_subtitle'], entry['uri'])

            self.reports[entry['uri']].entries.append(ReportEntry(entry['title'], entry['message_body'],
                                                                  entry['entry_id'], entry['actions']))


class MailHandler(Handler):
    def __init__(self, jobargs, period, period_name):
        super().__init__(jobargs, "mail", period, period_name)

    def make_report(self):
        self.subject = self.period_name + " namlat reports " + time.strftime("%d %b %Y", time.gmtime(time.time()))
        self.mail_body = jinja_env.get_template(MAIL_TEMPLATE).render(reports=self.reports.values(), subject=self.subject,
                                                                      url=context.config['server'])
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


