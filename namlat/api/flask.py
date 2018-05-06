from flask import Flask, Response, request, url_for, render_template, send_from_directory  # , json
import jinja2
from threading import Lock, Thread
import xaled_utils.json_serialize as json
from namlat.config import JINJA2_TEMPLATE_DIR, WEB_STATIC_DIR
from namlat.context import context
from namlat.updates import get_update_from_request_dict
from namlat.modules import get_module_route_rules
import namlat.api.server as server
import logging

logger = logging.getLogger(__name__)

data_lock = Lock()  # Todo: threadsafe only if there is one server/master that is jobless
APP_ROOT = ''
# CORE_PATH = '/core'
MODULES_PATH = ''
app = Flask(__name__)


def server_main(args=None):
    if args is not None:
        from namlat import load_data
        load_data(args)
    if 'modules' in context.config:
        for module_ in context.config['modules']:
            try:
                module_path = APP_ROOT + MODULES_PATH + '/' + module_
                module_rules = get_module_route_rules(module_)
                for rule in module_rules:
                    app.add_url_rule(module_path + rule['rule'], rule['endpoint'], rule['view_func'], **rule['options'])
                logger.debug("added %d flask rule for module: %s.", len(module_rules), module_path)
            except:
                logger.error("Unable to load gui routes for module: %s", module_, exc_info=True)
    my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([JINJA2_TEMPLATE_DIR]),
    ])
    app.jinja_loader = my_loader
    app.run('0.0.0.0', debug=True, threaded=True, use_reloader=False)


def server_main_threaded():
    thread = Thread(target=server_main)
    thread.setDaemon(True)
    thread.start()


def error_400():
    logger.error("error_400")
    resp = Response('{}', status=400, mimetype='application/json')
    return resp


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route(APP_ROOT + "/")
@app.route(APP_ROOT + "/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return render_template("site_map.html", links=links)


@app.route(APP_ROOT + '/namlat/ping', methods=['POST'])
def ping():
    # with data_lock:
    logger.debug("received ping request")
    if 'node_name' in request.form:
        resp_body = json.dumps({"ping": server.ping(request.form['node_name'])})
        resp = Response(resp_body, status=200, mimetype='application/json')
        return resp
    else:
        logger.warning("'node_name' param is not in the request data")
        return error_400()


@app.route(APP_ROOT + '/namlat/pull', methods=['POST'])
def pull():
    logger.debug("received pull request")
    try:
        # data_lock.acquire()
        if 'node_name' in request.form:
            # last_commit_id = request.form['last_commit_id']
            node_name = request.form['node_name']
            mail_bag = server.pull(node_name)
            resp_body = json.dumps({"mail_bag": mail_bag})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            logger.warning("'last_commit_id' param is not in the request data")
            return error_400()
    except Exception as e:
        logger.error("error in pull request: %s", str(e), exc_info=True)
        return error_400()
    # finally:
    #     data_lock.release()


@app.route(APP_ROOT + '/namlat/update', methods=['POST'])
def update():
    logger.debug("received client update")
    try:
        # data_lock.acquire()
        if 'outgoing_mail' in request.form:
            logger.debug("update request: %s", request.form)

            # old_commit_id = request.form['old_commit_id']
            outgoing_mail = json.loads(request.form['outgoing_mail'])
            # update_request_dict = json.loads(request.form['update'])
            # update = get_update_from_request_dict(update_request_dict)
            commit_id = server.updati(outgoing_mail)
            logger.debug("returning commit_id=%s", commit_id)
            resp_body = json.dumps({"OK": True})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            logger.warning("'outgoing_mail' params are not in the request data")
            return error_400()
    except Exception as e:
        logger.error("error in update request: %s", str(e), exc_info=True)
        return error_400()
    # finally:
    #     data_lock.release()


# @app.route(APP_ROOT + '/namlat/sync', methods=['GET'])
# def sync():
#     logger.debug("received client sync")
#     try:
#         data_lock.acquire()
#         sync_data, sync_logs = server.sync()
#         resp_body = json.dumps({'sync_data':sync_data, 'sync_logs':sync_logs})
#         resp = Response(resp_body, status=200, mimetype='application/json')
#         return resp
#     except Exception as e:
#         logger.error("error in update request: %s", str(e), exc_info=True)
#         return error_400()
#     finally:
#         data_lock.release()


@app.route(APP_ROOT + '/namlat/createNode', methods=['POST'])
def create_node():
    logger.debug("received client createNode")
    try:
        # data_lock.acquire()
        if 'gw' in request.form and 'public_key' in request.form and 'node_name' in request.form:  # and 'address' in request.form \
            # gw = request.form['gw']
            # address = request.form['address']
            public_key = request.form['public_key']
            node_name = request.form['node_name']
            accepted = server.create_node(public_key, node_name)
            # if accepted:
            #     sync_data, sync_logs = server.sync()
            # else:
            #     sync_data, sync_logs = None, None
            # logger.debug("response: %s", {'accepted': accepted, 'sync_data':sync_data, 'sync_logs':sync_logs})
            resp_body = json.dumps({'accepted': accepted}) #, 'sync_data': sync_data, 'sync_logs': sync_logs})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            logger.warning("bad parameters!")
            return error_400()
    except Exception as e:
        logger.error("error in update request: %s", str(e), exc_info=True)
        return error_400()
    # finally:
        # data_lock.release()


@app.route(APP_ROOT + '/plugins/<path:path>')
@app.route(APP_ROOT + '/bower_components/<path:path>')
@app.route(APP_ROOT + '/dist/<path:path>')
@app.route(APP_ROOT + '/css/<path:path>')
@app.route(APP_ROOT + '/js/<path:path>')
@app.route(APP_ROOT + '/img/<path:path>')
def static_ressource(path):
    # logger.debug("path:%s", path)
    dir = request.path.split('/')[1]
    # logger.debug("dir: %s", dir)
    # logger.debug("sent: %s, %s", WEB_STATIC_DIR + dir, path)
    return send_from_directory(WEB_STATIC_DIR + dir, path)


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    from xaled_utils.time_ops import epoch_to_iso8601
    return epoch_to_iso8601(date)
