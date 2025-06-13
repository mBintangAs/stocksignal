from tasks import run_get_signal

from flask import Flask, jsonify
from flask_cors import CORS

from celery.result import AsyncResult
from celery_worker import app as celery_app
# Inisialisasi Flask
app = Flask(__name__)

CORS(app)

@app.get('/signal')
def get_signal():
     # Dapatkan status worker
    i = celery_app.control.inspect()
    reserved = i.reserved()
    active = i.active()
    # Gabungkan reserved + active (task yang sedang menunggu dan task yang sedang berjalan)
    task_count = 0
    if reserved:
        for k, v in reserved.items():
            task_count += len(v)
    if active:
        for k, v in active.items():
            task_count += len(v)

    if task_count > 0:
        return jsonify({"message": "Processing", 'status': 'processing'})

    task = run_get_signal.delay()
    return jsonify({"task_id": task.id, "status": "processing"})

@app.get('/status/<task_id>')
def task_status(task_id):
    res = AsyncResult(task_id, app=celery_app)
    if res.state == 'PENDING':
        return jsonify({"status": res.state}), 202
    elif res.state == 'SUCCESS':
        return jsonify({"status": res.state, "result": res.result}), 200
    else:
        return jsonify({"status": res.state}), 200


if __name__ == '__main__':
    app.run(debug=True)