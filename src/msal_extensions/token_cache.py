import sys
import os
import tempfile
import time
import msal

if sys.platform.startswith('win'):
    from ._windows import _WindowsTokenCache
elif sys.platform.startswith('darwin'):
    from ._osx import _OSXTokenCache


def get_protected_token_cache(enforce_encryption=False, **kwargs):
    if sys.platform.startswith('win'):
        return _WindowsTokenCache(**kwargs)
    elif sys.platform.startswith('darwin'):
        return _OSXTokenCache(**kwargs)
    elif enforce_encryption:
        raise RuntimeError('no protected token cache for platform {}'.format(sys.platform))
    else:
        return FileTokenCache(**kwargs)


class FileTokenCache(msal.SerializableTokenCache):
    # TODO: Find correct location for this file
    DEFAULT_FILE_LOCATION = os.path.join(tempfile.gettempdir(), "msal.cache.txt")

    def __init__(self, file_location=None):
        self._file_location = file_location or FileTokenCache.DEFAULT_FILE_LOCATION
        self._last_sync = 0

    def add(self, event, **kwargs):
        super(FileTokenCache, self).add(event, **kwargs)
        self._write()

    def update_rt(self, rt_item, new_rt):
        super(FileTokenCache, self).update_rt(rt_item, new_rt)
        self._write()

    def remove_rt(self, rt_item):
        super(FileTokenCache, self).remove_rt(rt_item)
        self._write()

    def find(self, credential_type, target=None, query=None):
        if self._has_state_changed():
            self._read()
        return super(_WindowsTokenCache, self).find(credential_type, target=target, query=query)

    def _write(self):
        with open(self._file_location, "w") as fh:
            fh.write(self.serialize())
        self._last_sync = int(time.time())

    def _read(self):
        with open(self._file_location, "r") as fh:
            self.deserialize(fh.read())
        self._last_sync = int(time.time())
