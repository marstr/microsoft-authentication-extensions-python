import os
import abc
from msal.application import PublicClientApplication, ConfidentialClientApplication
from .token_cache import get_protected_token_cache

_DEFAULT_CLIENT_ID = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

class ProviderUnavailableError(ValueError):
    pass


class TokenProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def available(self):
        # type: () -> bool
        raise NotImplementedError()

    @abc.abstractmethod
    def get_token(self, scopes=None, username=None):
        # type: (*str) -> {str:str}
        raise NotImplementedError()


class TokenProviderChain(TokenProvider):
    def __init__(self, *args):
        self._links = list(args)

    def available(self):
        return any((item for item in self._links if item.available()))

    def get_token(self, scopes=None, username=None):
        return next((item.get_token(scopes=scopes) for item in self._links if item.available()))


class SharedTokenCacheProvider(TokenProvider):

    def __init__(self, client_id=None, cache_location=None):
        client_id = client_id or _DEFAULT_CLIENT_ID
        token_cache = get_protected_token_cache(cache_location=cache_location)
        self._app = PublicClientApplication(client_id=client_id, token_cache=token_cache)

    def available(self):
        return any(self._get_accounts())

    def get_token(self, scopes=None, username=None):
        accounts = self._get_accounts(username=username)
        if any(accounts):
            active_account = accounts[0]
            return self._app.acquire_token_silent(scopes=scopes, account=active_account)
        raise ProviderUnavailableError()

    def _get_accounts(self, username=None):
        return self._app.get_accounts(username=username)


class ServicePrincipalProvider(TokenProvider):

    def __init__(self, client_id=None, client_secret=None):
        client_id = client_id or os.getenv('AZURE_CLIENT_ID')
        client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')

        self._app = ConfidentialClientApplication(
            client_id=client_id,
            client_secret=client_secret,
        )

    def available(self):
        """ Always returns true, because if it was able to be instantiated, it is available for use."""
        return True

    def get_token(self, scopes=None):
        return self._app.acquire_token_for_client(scopes=scopes)


DEFAULT_TOKEN_CHAIN = TokenProviderChain(
    SharedTokenCacheProvider())
