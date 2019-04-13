import sys
import os
import msal
import time
from ._cache_lock import CrossPlatLock

class ProtectedTokenCache(msal.SerializableTokenCache):
    def __init__(self, **kwargs):
        if sys.platform.startswith('win'):
            self._underlyer = _WindowsTokenCache(**kwargs)
        else:
            raise Exception('unsupported platform {}'.format(sys.platform))

    def add(self, event, **kwargs):
        self._underlyer.add(event, **kwargs)

    def update_rt(self, rt_item, new_rt):
        self._underlyer.update_rt(rt_item, new_rt)
    
    def remove_rt(self, rt_item):
        self._underlyer.remove_rt(rt_item)
    
    def find(self, credential_type, target=None, query=None):
        return self._underlyer.find(credential_type, target=target, query=query)

    
class _WindowsTokenCache(msal.SerializableTokenCache):
    DEFAULT_CACHE_LOCATION = os.path.join(os.getenv('LOCALAPPDATA'), '.IdentityService', 'msal.cache')
    DEFAULT_ENTROPY = ''

    def __init__(self, **kwargs):
        from ._windows import WindowsDataProtectionAgent
        super(_WindowsTokenCache, self).__init__()

        self._cache_location = _WindowsTokenCache.DEFAULT_CACHE_LOCATION # type: str
        if 'cache_location' in kwargs:
            self._cache_location = kwargs['cache_location']
        self._lock_location = self._cache_location + '.lockfile'

        entropy = _WindowsTokenCache.DEFAULT_ENTROPY
        if 'entropy' in kwargs:
           entropy = kwargs['entropy']
        self._dp_agent = WindowsDataProtectionAgent(entropy=entropy)
        self._last_sync = 0 # _last_sync is a Unixtime

    def _has_state_changed(self):
        # type: () -> Bool
        return self.has_state_changed or self._last_sync < os.path.getmtime(self._cache_location)

    def add(self, event, **kwargs):
        super(_WindowsTokenCache, self).add(event, **kwargs)
        self._write()

    def update_rt(self, rt_item, new_rt):
        super(_WindowsTokenCache, self).update_rt(rt_item, new_rt)
        self._write()

    def remove_rt(self, rt_item):
        super(_WindowsTokenCache, self).remove_rt(rt_item)
        self._write()

    def find(self, credential_type, target=None, query=None):
        if self._has_state_changed():
            self._read()
        return super(_WindowsTokenCache, self).find(credential_type, target=target, query=query)

    def _write(self):
        with CrossPlatLock(self._lock_location), open(self._cache_location, 'wb') as fh:
            fh.write(self._dp_agent.protect(self.serialize()))
        self._last_sync = int(time.time())

    def _read(self):
        with CrossPlatLock(self._lock_location), open(self._cache_location, 'rb') as fh:
            cipher_text = fh.read()
            contents = self._dp_agent.unprotect(cipher_text)
            self.deserialize(contents)
        self._last_sync = int(time.time())
