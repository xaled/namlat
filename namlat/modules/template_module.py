import logging as _logging
from flask import render_template
from namlat.context import context
from namlat.utils.flask import FlaskRulesContainer

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
def module_index():
    return render_template("module_index.html", modul=__name__)