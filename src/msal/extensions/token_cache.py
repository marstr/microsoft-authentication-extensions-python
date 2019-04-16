import sys
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
        elif sys.platform.startswith('darwin'):
            self._underlyer = _OSXTokenCache(**kwargs)
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



