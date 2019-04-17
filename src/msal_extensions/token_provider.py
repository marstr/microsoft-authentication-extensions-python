import os
import abc
from msal.application import PublicClientApplication
from .token_cache import ProtectedTokenCache


class TokenProvider(abc.ABC):
    @abc.abstractmethod
    def available(self):
        # type: () -> bool
        pass

    @abc.abstractmethod
    def get_token(self, scopes=None):
        # type: (*str) -> {str:str}
        pass


class TokenProviderChain(TokenProvider):
    def __init__(self, *args):
        self._links = list(args)

    def available(self):
        return any((item for item in self._links if item.available()))

    def get_token(self, scopes=None):
        return next((item.get_token(scopes=scopes) for item in self._links if item.available()))


class SharedTokenCacheProvider(TokenProvider):
    def __init__(self, client_id, username=None, cache_location=None):
        cache_location = cache_location or os.path.join(os.getenv('LOCALAPPDATA'), 'msal.cache')
        token_cache = ProtectedTokenCache(cache_location=cache_location)
        self._app = PublicClientApplication(client_id=client_id, token_cache=token_cache)
        self._username = username

    def available(self):
        return any(self._get_accounts())

    def get_token(self, scopes=None):
        accounts = self._get_accounts()
        if any(accounts):
            active_account = accounts[0]
        return self._app.acquire_token_silent(scopes=scopes, account=active_account)

    def _get_accounts(self):
        return self._app.get_accounts(username=self._username)


