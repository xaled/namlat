import time
import logging as _logging
import namlat.report as nr
from namlat.modules import AbstractNamlatJob


logger = _logging.getLogger(__name__)


class DummyJob(AbstractNamlatJob):
    def execute(self):
        logger.info("executing DummyJob")
        report = self.get_report("dummy", "dummy", nr.NOTIFICATION_HANDLERS)

        self.report("dummy", 'dummy report entry in %f' % (time.time()), report=report)



