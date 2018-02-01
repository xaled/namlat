import time
import logging as _logging
import namlat.report as nr
from namlat.modules import AbstractNamlatJob


logger = _logging.getLogger(__name__)


class DummyJob(AbstractNamlatJob):
    def execute(self):
        logger.info("executing DummyJob")
        report_maker = nr.NewReportMaker(self.module_, "dummy", "Dummy report for host %s %f" % (self.context.address, time.time()) ,
                                         handlers=nr.NOTIFICATION_HANDLERS, report_subtitle='subtitle')

        self.report("dummy", 'dummy report entry', report_maker=report_maker)



