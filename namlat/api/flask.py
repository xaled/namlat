from flask import Flask, Response, json, request
from threading import Lock, Thread
from namlat.updates import get_update_from_request_dict
import namlat.api.server as server
import logging
logger = logging.getLogger(__name__)

data_lock = Lock() # Todo: threadsafe only if there is one server/master that is jobless
app = Flask(__name__)


def server_main(args=None):
    if args is not None:
        from namlat import load_data
        load_data(args)
    app.run()


def server_main_threaded():
    thread = Thread(target=server_main)
    thread.setDaemon(True)
    thread.start()


def error_400():
    logger.error("error_400")
    resp = Response('{}', status=400, mimetype='application/json')
    return resp


@app.route('/namlat/pull', methods=['POST'])
def api_pull():
    logger.debug("received pull request")
    try:
        data_lock.acquire()
        if 'last_commit_id' in request.form:
            last_commit_id = request.form['last_commit_id']
            updates_log = server.pull(last_commit_id)
            resp_body = json.dumps({"updates_log":updates_log})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            logger.warning("'last_commit_id' param is not in the request data")
            return error_400()
    except Exception as e:
        logger.error("error in pull request: %s", str(e), exc_info=True)
        return error_400()
    finally:
        data_lock.release()


@app.route('/namlat/update', methods=['POST'])
def api_update():
    logger.debug("received client update")
    try:
        data_lock.acquire()
        if 'old_commit_id' in request.form and 'update' in request.form:
            old_commit_id = request.form['old_commit_id']
            logger.debug(request.form['update'])
            update_request_dict = json.loads(request.form['update'])
            update = get_update_from_request_dict(update_request_dict)
            commit_id = server.updati(old_commit_id, update)
            logger.debug("returning commit_id=%s", commit_id)
            resp_body = json.dumps({"commit_id":commit_id})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            logger.warning("'old_commit_id' or 'update' params are not in the request data")
            return error_400()
    except Exception as e:
        logger.error("error in update request: %s", str(e), exc_info=True)
        return error_400()
    finally:
        data_lock.release()


@app.route('/namlat/sync', methods=['GET'])
def api_sync():
    logger.debug("received client sync")
    try:
        data_lock.acquire()
        sync_data, sync_logs = server.sync()
        resp_body = json.dumps({'sync_data':sync_data, 'sync_logs':sync_logs})
        resp = Response(resp_body, status=200, mimetype='application/json')
        return resp
    except Exception as e:
        logger.error("error in update request: %s", str(e), exc_info=True)
        return error_400()
    finally:
        data_lock.release()


@app.route('/namlat/createNode', methods=['POST'])
def api_create_node():
    logger.debug("received client sync")
    try:
        data_lock.acquire()
        if 'gw' in request.form and 'public_key' in request.form and 'node_name' in request.form: # and 'address' in request.form \
            # gw = request.form['gw']
            # address = request.form['address']
            public_key = request.form['public_key']
            node_name = request.form['node_name']
            accepted = server.create_node(public_key, node_name)
            if accepted:
                sync_data, sync_logs = server.sync()
            else:
                sync_data, sync_logs = None, None
            # logger.debug("response: %s", {'accepted': accepted, 'sync_data':sync_data, 'sync_logs':sync_logs})
            resp_body = json.dumps({'accepted': accepted, 'sync_data':sync_data, 'sync_logs':sync_logs})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            logger.warning("bad parameters!")
            return error_400()
    except Exception as e:
        logger.error("error in update request: %s", str(e), exc_info=True)
        return error_400()
    finally:
        data_lock.release()