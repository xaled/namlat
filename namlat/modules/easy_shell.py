import logging as _logging
from flask import render_template
from namlat.context import context
from namlat.utils.flask import FlaskRulesContainer
from xaled_utils.commands import run_command_ex1

flask_rule_container = FlaskRulesContainer()
logger = _logging.getLogger(__name__)
with context.localdb:
    if 'modules' not in context.localdb:
        context.localdb['modules'] = dict()
    if __name__ not in context.localdb['modules']:
        context.localdb['modules'][__name__] = {}
module_db = context.localdb['modules'][__name__]
module_config = context.config['modules'][__name__]


def mail_hook():
    pass


def get_flask_rules():
    return flask_rule_container.rules


@flask_rule_container.route('/')
def easy_shell_index():
    buttons = list()
    if 'buttons' in module_config:
        for button in module_config['buttons'].values():
            buttons.append(button['name'])

    return render_template("easy_shell/list_buttons.html", buttons=buttons)


@flask_rule_container.route('/buttons/<button>')
def button_view(button):
    return_code, output = run_command_ex1(module_config['buttons'][button]['cmd_vector'])
    return render_template("easy_shell/button_view.html", button=button, output=output.decode(), return_code=return_code)

