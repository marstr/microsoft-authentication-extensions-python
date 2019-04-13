import os
import msal
import time
from ._cache_lock import CrossPlatLock
from ._windows import WindowsDataProtectionAgent

class WindowsTokenCache(msal.SerializableTokenCache):
    DEFAULT_CACHE_LOCATION = os.path.join(os.getenv('LOCALAPPDATA'), '.IdentityService', 'msal.cache')
    DEFAULT_ENTROPY = ''

    def __init__(self, **kwargs):
        super(WindowsTokenCache, self).__init__()

        self._cache_location = WindowsTokenCache.DEFAULT_CACHE_LOCATION # type: str
        if 'cache_location' in kwargs:
            self._cache_location = kwargs['cache_location']
        self._lock_location = self._cache_location + '.lockfile'

        entropy = WindowsTokenCache.DEFAULT_ENTROPY
        if 'entropy' in kwargs:
           entropy = kwargs['entropy']
        self._dp_agent = WindowsDataProtectionAgent(entropy=entropy)
        self._last_touch = 0 # _last_touch is a Unixtime

    def _has_state_changed(self):
        # type: () -> Bool
        return self.has_state_changed or self._last_touch < os.path.getmtime(self._cache_location)

    def add(self, event, **kwargs):
        super(WindowsTokenCache, self).add(event, **kwargs)
        self._write()

    def update_rt(self, rt_item, new_rt):
        super(WindowsTokenCache, self).update_rt(rt_item, new_rt)
        self._write()

    def remove_rt(self, rt_item):
        super(WindowsTokenCache, self).remove_rt(rt_item)
        self._write()

    def find(self, credential_type, target=None, query=None):
        if self._has_state_changed():
            self._read()
        return super(WindowsTokenCache, self).find(credential_type, target=target, query=query)

    def _write(self):
        with CrossPlatLock(self._lock_location), open(self._cache_location, 'wb') as fh:
            fh.write(self._dp_agent.protect(self.serialize()))

    def _read(self):
        with CrossPlatLock(self._lock_location), open(self._cache_location, 'rb') as fh:
            cipher_text = fh.read()
            contents = self._dp_agent.unprotect(cipher_text)
            self.deserialize(contents)
            


