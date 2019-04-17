import sys
import pytest
import msal

if not sys.platform.startswith('darwin'):
    pytest.skip('skipping OSX-only tests', allow_module_level=True)
else:
    from msal_extensions.token_cache import _OSXTokenCache
    from msal_extensions._osx import KeychainItemNotFoundError


def test_read_cache():
    try:
        subject = _OSXTokenCache()
        tokens = subject.find(msal.TokenCache.CredentialType.ACCESS_TOKEN)
        assert len(tokens) > 0
    except KeychainItemNotFoundError:
        pytest.skip('could not find the MSAL Cache (try logging in using MSAL)')

