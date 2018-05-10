import logging as _logging
from flask import render_template
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
try: module_config = context.config['modules'][__name__]
except: module_config = None


class EasyShellExecutionJob(AbstractNamlatJob):
    def execute(self):
        logger.info("executing EasyShellExecutionJob")
        report = self.get_report("easyshell", "easyshell_executions", self.kwargs['notify_handlers'],
                                 report_title="EasyShell Executions for host " + self.context.node_name)
        for command in self.kwargs['commands']:
            logger.debug("Excuting command :%s", command['name'])
            try:
                return_code, output = run_command_ex1(command['cmd_vector'])
                output = output.decode(errors="replace")
                report.append_report_entry("Command %s executed" % command['name'],
                                           "cmd: %s\n return_code: %s\n output:%s" %
                                           (' '.join(command['cmd_vector']), return_code, output))
            except:
                logger.error("Error while executing command: %s", command)
                report.append_report_entry("Command %s failed to execute" % command['name'],
                                           "cmd: %s" % (' '.join(command['cmd_vector'])))

        report.send_report()


def _get_button(button_name):
    if 'buttons' in module_config:
        for button in module_config['buttons']:
            if button['name'] == button_name:
                return button
    return None


def mail_hook():
    pass


def get_flask_rules():
    return flask_rule_container.rules


@flask_rule_container.route('/')
def easy_shell_index():
    buttons = list()
    if 'buttons' in module_config:
        for button in module_config['buttons']:
            buttons.append(button['name'])

    return render_template("easy_shell/list_buttons.html", title="EasyShell", section_title="Buttons", buttons=buttons)


@flask_rule_container.route('/buttons/<button_name>')
def button_view(button_name):
    button = _get_button(button_name)
    return_code, output = run_command_ex1(button['cmd_vector'])
    output = output.decode(errors="replace")
    return render_template("easy_shell/button_view.html", title="EasyShell", button=button_name,
                           output=output, return_code=return_code)
