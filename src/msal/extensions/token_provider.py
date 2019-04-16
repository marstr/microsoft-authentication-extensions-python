import os
import abc
from msal.application import PublicClientApplication


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
    def __init__(self, client_id, username=None):
        self._app = PublicClientApplication(client_id=client_id)
        self._username = username

    def available(self):
        return any(self._get_accounts())

    def get_token(self, scopes=None):
        accounts = self._get_accounts()
        if any(accounts):
            active_account = accounts[0]
        self._app.acquire_token_silent(scopes=scopes, account=active_account)

    def _get_accounts(self):
        return self._app.get_accounts(username=self._username)


