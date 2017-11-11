from flask import Flask, Response, json, request
from threading import Lock, Thread
from namlat import pull_server, update_server
import logging
logger = logging.getLogger(__name__)


def app_thread(): app.run()
data_lock = Lock()
app = Flask(__name__)
thread = Thread(target=app_thread)


def error_400():
    resp = Response('{}', status=400, mimetype='application/json')
    return resp


@app.route('/namlat/pull', methods=['POST'])
def api_pull():
    try:
        data_lock.acquire()
        if 'last_commit_id' in request.form:
            last_commit_id = request.form['last_commit_id']
            updates_log = pull_server(last_commit_id)
            resp_body = json.dumps({"updates_log":updates_log})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            return error_400
    except:
        pass
    finally:
        data_lock.release()


@app.route('/namlat/update', methods=['POST'])
def api_update():
    try:
        data_lock.acquire()
        if 'old_commit_id' in request.form and 'update' in request.form:
            old_commit_id = request.form['old_commit_id']
            update = json.loads(request.form['update'])
            commit_id = update_server(old_commit_id, update)
            resp_body = json.dumps({"commit_id":commit_id})
            resp = Response(resp_body, status=200, mimetype='application/json')
            return resp
        else:
            return error_400
    except:
        pass
    finally:
        data_lock.release()