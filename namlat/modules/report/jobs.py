import time
import logging as _logging
from namlat.context import context
from namlat.modules import AbstractNamlatJob
logger = _logging.getLogger(__name__)


class ReportJob(AbstractNamlatJob):
    def init_job(self):
        pass

    def execute(self):
        from namlat.modules.report.common import process_new_entries
        logger.info("executing ReportJob")
        process_new_entries()
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
            self.send_report_entry("%d handlers executed" % len(executed_handlers), str(executed_handlers))
        # save changes
        context.localdb.save()

    def get_report_handlers(self):
        from namlat.modules.report.handlers import MailHandler, SmsHandler, TelegramHandler
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
