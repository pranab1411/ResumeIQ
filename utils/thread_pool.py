"""
utils/thread_pool.py
Asynchronous Task Executor for PyQt6 UI responsiveness.
"""

from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from utils.logger import logger

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(res)
        except Exception as e:
            import sys, traceback
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()

class AsyncExecutor:
    def __init__(self):
        self.thread_pool = QThreadPool.globalInstance()

    def run_async(self, fn, *args, on_result=None, on_error=None, on_finished=None, **kwargs):
        worker = Worker(fn, *args, **kwargs)
        if on_result:
            worker.signals.result.connect(on_result)
        if on_error:
            worker.signals.error.connect(on_error)
        if on_finished:
            worker.signals.finished.connect(on_finished)
        self.thread_pool.start(worker)

async_executor = AsyncExecutor()
