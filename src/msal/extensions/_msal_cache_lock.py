import os
import datetime
import time
import psutil

class CrossPlatLock(object):
    RETRY_WAIT = datetime.timedelta(milliseconds=100)
    RETRY_COUNT = int(datetime.timedelta(minutes=1).total_seconds() / RETRY_WAIT.total_seconds())

    def __init__(self, lockfile_path):
        self._lockpath = lockfile_path

    def __enter__(self):
        pid = os.getpid()
        proc = psutil.Process(pid)
        lockdir = os.path.dirname(self._lockpath)
        os.makedirs(lockdir, exist_ok=True)

        for _ in range(CrossPlatLock.RETRY_COUNT):
            try:
                self._fh = open(self._lockpath, 'wb+', buffering=0)
                self._fh.write('{} {}'.format(pid, proc.name()).encode('utf-8'))
                break
            except PermissionError:
                time.sleep(CrossPlatLock.RETRY_WAIT.total_seconds())
        

    def __exit__(self, *args):
        self._fh.close()
        os.remove(self._lockpath)
