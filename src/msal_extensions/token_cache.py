import sys
import os
import tempfile
import time
import msal

if sys.platform.startswith('win'):
    from ._windows import _WindowsTokenCache
elif sys.platform.startswith('darwin'):
    from ._osx import _OSXTokenCache


class ProtectedTokenCache(msal.SerializableTokenCache):
    """Decorates platform specific implementations of TokenCache which use OS provided encryption mechanisms."""
    def __init__(self, **kwargs):
        if sys.platform.startswith('win'):
            self._underlyer = _WindowsTokenCache(**kwargs)
            self._is_protected = True
        elif sys.platform.startswith('darwin'):
            self._underlyer = _OSXTokenCache(**kwargs)
            self._is_protected = True
        else:
            self._underlyer = FileTokenCache(**kwargs)
            self._is_protected = False

    def add(self, event, **kwargs):
        self._underlyer.add(event, **kwargs)

    def update_rt(self, rt_item, new_rt):
        self._underlyer.update_rt(rt_item, new_rt)
    
    def remove_rt(self, rt_item):
        self._underlyer.remove_rt(rt_item)
    
    def find(self, credential_type, target=None, query=None):
        return self._underlyer.find(credential_type, target=target, query=query)

    @property
    def is_protected(self):
        """On platforms where no implementation exists to protect """
        return self._is_protected


class FileTokenCache(msal.SerializableTokenCache):
    # TODO: Find correct location for this file
    DEFAULT_FILE_LOCATION = os.join(tempfile.gettempdir(), "msal.cache.txt")

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
