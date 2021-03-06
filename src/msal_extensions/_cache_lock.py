import os
import datetime
import time
import psutil
import portalocker


class CrossPlatLock(object):
    TIMEOUT = datetime.timedelta(minutes=1)
    RETRY_WAIT = datetime.timedelta(milliseconds=100)
    RETRY_COUNT = int(TIMEOUT.total_seconds() / RETRY_WAIT.total_seconds())

    def __init__(self, lockfile_path):
        self._lockpath = lockfile_path

    def __enter__(self):
        pid = os.getpid()
        proc = psutil.Process(pid)
        lock_dir = os.path.dirname(self._lockpath)
        if not os.path.exists(lock_dir):
            os.makedirs(lock_dir)

        self._fh = open(self._lockpath, 'wb+', buffering=0)
        portalocker.lock(self._fh, portalocker.LOCK_EX)
        self._fh.write('{} {}'.format(pid, proc.name()).encode('utf-8'))

    def __exit__(self, *args):
        self._fh.close()
        try:
            os.remove(self._lockpath)
        except PermissionError:
            pass
