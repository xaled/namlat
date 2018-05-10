import logging as _logging
import os
from namlat.config import NAMLAT_HOME_DIR, DATA_DIR
from namlat.context import context
from namlat.utils.flask import FlaskRulesContainer
from namlat.modules import AbstractNamlatJob
from easilyb.commands import run_command_ex1

flask_rule_container = FlaskRulesContainer()
logger = _logging.getLogger(__name__)
with context.localdb:
    if 'modules' not in context.localdb:
        context.localdb['modules'] = dict()
    if __name__ not in context.localdb['modules']:
        context.localdb['modules'][__name__] = {}
module_db = context.localdb['modules'][__name__]
BACKUP_DIR = os.path.join(NAMLAT_HOME_DIR, "backup")
os.makedirs(BACKUP_DIR)


class BackupJob(AbstractNamlatJob):
    def execute(self):
        logger.info("BackupJob")
        report = self.get_report("default", "default", self.kwargs['notify_handlers'],
                                 report_title="Backup executions" + self.context.node_name)
        with context.localdb:
            if self.kwargs['period'] not in module_db:
                module_db[self.kwargs['period']] = {"last_backup": -1}
        period_object = module_db[self.kwargs['period']]
        new_backup = period_object["last_backup"] + 1
        if new_backup >= self.kwargs['max_backups'] or new_backup < 0:
            new_backup = 0
        try:
            tarfilename = "backup_%s_%d.tag.gz" % (self.kwargs['period'], new_backup)
            tarfilepath = os.path.join(BACKUP_DIR, tarfilename)
            if os.path.isfile(tarfilepath):
                os.unlink(tarfilepath)
            return_code, output = run_command_ex1(['tar', '-zvcf', tarfilepath, DATA_DIR])
            output = output.decode(errors="replace")
            report.append_report_entry("Buckup executed", output)
        except:
            logger.error("Error while executing Backup")
            report.append_report_entry("Error while executing Backup.", "")
            with context.localdb:
                period_object["last_backup"] = new_backup
        report.send_report()
