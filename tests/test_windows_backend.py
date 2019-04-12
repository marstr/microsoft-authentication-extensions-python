import sys
import os
import pytest
import uuid
import json
import msal.token_cache as msaltc

if not sys.platform.startswith('win'):
    pytest.skip('skipping windows-only tests', allow_module_level=True)
else:
    from msal.extensions._windows import WindowsDataProtectionAgent


def test_dpapi_roundtrip_with_entropy():
    subject_without_entropy = WindowsDataProtectionAgent()
    subject_with_entropy = WindowsDataProtectionAgent(entropy=uuid.uuid4().hex)

    test_cases = [
        '',
        'lorem ipsum',
        'lorem-ipsum',
        '<Python>',
        uuid.uuid4().hex,
    ]

    for tc in test_cases:    
        ciphered = subject_with_entropy.protect(tc)
        assert ciphered != tc

        got = subject_with_entropy.unprotect(ciphered)
        assert got == tc

        ciphered = subject_without_entropy.protect(tc)
        assert ciphered != tc

        got = subject_without_entropy.unprotect(ciphered)
        assert got == tc


def test_read_msal_cache():
    try:
        msal_location = os.path.join(os.getenv('LOCALAPPDATA'), 'msal.cache')
        with open(msal_location, mode='rb') as fh:
            contents = fh.read()
    except FileNotFoundError:
        pytest.skip('could not find the msal.cache file (try logging in using MSAL)')
    
    subject = WindowsDataProtectionAgent()
    raw = subject.unprotect(contents)
    assert raw != ""

    cache = msaltc.SerializableTokenCache()
    cache.deserialize(raw)
    access_tokens = cache.find(msaltc.TokenCache.CredentialType.ACCESS_TOKEN)
    assert len(access_tokens) > 0
    
