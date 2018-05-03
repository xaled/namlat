import time
import subprocess
import os
import logging as _logging
import namlat.report as nr
import namlat.updates as nu
from namlat.modules import AbstractNamlatJob

logger = _logging.getLogger(__name__)


class GitJob(AbstractNamlatJob):
    def init_job(self):
        pass

    def execute(self):
        logger.info("executing GitJob")
        report = self.get_report("gitstatus", "gitstatus", nr.DAILY_MAIL_HANDLERS,
                                 report_title="Git cron report for host " + self.context.node_name)
        for root_dir in self.kwargs['root-dirs']:
            logger.debug("processing root-dir:%s", root_dir)
            sub_dirs = [os.path.join(root_dir, child) for child in os.listdir(root_dir) if
                        os.path.isdir(os.path.join(root_dir, child))]
            for dir in sub_dirs:
                if _is_git(dir):
                    logger.debug("processing git repository: %s", dir)
                    remote_status, remote_message = _get_remote_status(dir)
                    logger.debug("%s: %s", dir, remote_message)
                    if not remote_status:
                        report.append_report_entry(dir, remote_message)
                    local_satus = _get_local_status(dir)
                    if not local_satus:
                        report.append_report_entry(dir, 'not all changes are commited')

        report.send_report()


def _get_cmd_output(command_vector):
    o, ec = subprocess.Popen(command_vector, stdout=subprocess.PIPE).communicate()
    return str(o), ec


def _git_cmd(dir, cmd, args):
    return _get_cmd_output(['git', '-C', dir, cmd] + args)


def _is_git(dir):
    return os.path.isdir(os.path.join(dir, '.git'))


def _get_remote_status(dir):
    o, ec = _git_cmd(dir, 'remote', ['update'])
    o, ec = _git_cmd(dir, 'status', ['-uno'])
    line = ''
    for l in o.split('\n'):
        if l.strip().startswith('Your branch'):
            line = l
            break
    if 'up-to-date' in line:
        synced = True
    else:
        synced = False
    return synced, line.strip()


def _get_local_status(dir):
    o, ec = _git_cmd(dir, 'status', [])
    if 'nothing to commit' in o:
        return True
    return False
