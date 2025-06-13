# filepath: /home/bintang/Dokumen/python/stocksignal/tasks.py
from celery_worker import app
from predict import  get_signal_logic # Buat fungsi ini di app.py

@app.task
def run_get_signal():
    return get_signal_logic()