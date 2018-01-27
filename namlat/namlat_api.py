from flask import Flask, Response, json, request
from threading import Lock, Thread
from namlat import pull_server, update_server, sync_server
import logging
logger = logging.getLogger(__name__)

data_lock = Lock()
app = Flask(__name__)


def app_thread():
    app.run()


def server_main():
    thread = Thread(target=app_thread)
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
            updates_log = pull_server(last_commit_id)
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
            update = json.loads(request.form['update'])
            commit_id = update_server(old_commit_id, update)
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
        sync_data, sync_logs = sync_server()
        resp = Response({'sync_data':sync_data, 'sync_logs':sync_logs}, status=200, mimetype='application/json')
        return resp
    except Exception as e:
        logger.error("error in update request: %s", str(e), exc_info=True)
        return error_400()
    finally:
        data_lock.release()