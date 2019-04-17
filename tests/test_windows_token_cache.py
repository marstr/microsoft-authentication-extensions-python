import sys
import os
import pytest
import msal


if not sys.platform.startswith('win'):
    pytest.skip('skipping windows-only tests', allow_module_level=True)
else:
    from msal_extensions.token_cache import _WindowsTokenCache


def test_read_cache():
    appdata_loc = os.getenv('LOCALAPPDATA')
    cache_locations = [
        os.path.join(appdata_loc, '.IdentityService', 'msal.cache'),  # this is where it's supposed to be
        os.path.join(appdata_loc, '.IdentityServices', 'msal.cache'),  # miscommunication about this being plural or not
        os.path.join(appdata_loc, 'msal.cache'),  # The earliest most naive builds used this locations
    ]

    found = False
    for loc in cache_locations:
        try:
            subject = _WindowsTokenCache(cache_location=loc)
            tokens = subject.find(msal.TokenCache.CredentialType.ACCESS_TOKEN)
            assert len(tokens) > 0
            found = True
            break
        except FileNotFoundError:
                pass
    if not found:
            pytest.skip('could not find the msal.cache file (try logging in using MSAL)')
