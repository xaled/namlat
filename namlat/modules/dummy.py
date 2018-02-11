import time
import logging as _logging
import namlat.report as nr
from namlat.modules import AbstractNamlatJob


logger = _logging.getLogger(__name__)


class DummyJob(AbstractNamlatJob):
    def execute(self):
        logger.info("executing DummyJob")
        # report_maker = nr.NewReportMaker(self.module_, "dummy", "Dummy report for host %s %f" % (self.context.node_name, time.time()) ,
        #                                  handlers=nr.NOTIFICATION_HANDLERS, report_subtitle='subtitle')
        # report_maker = nr.NewReportMaker(self.data, self.module_, "dummy", handlers=nr.NOTIFICATION_HANDLERS)
        report_maker = self.get_report_maker("dummy", nr.NOTIFICATION_HANDLERS)

        self.report("dummy", 'dummy report entry in %f' % (time.time()), report_maker=report_maker)



