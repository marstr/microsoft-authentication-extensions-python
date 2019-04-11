import sys
import pytest
import uuid

if not sys.platform.startswith('win'):
    pytest.skip('skipping windows-only tests', allow_module_level=True)
else:
    from msal.extensions._windows import WindowsDataProtectionAgent


def test_dpapi_roundtrip_no_entropy():
    subject = WindowsDataProtectionAgent()

    want = uuid.uuid4().hex
    ciphered = subject.protect(want)
    assert ciphered != want
    got = subject.unprotect(ciphered)
    assert got == want


def test_dpapi_roundtrip_with_entropy():
    subject = WindowsDataProtectionAgent(entropy=uuid.uuid4().hex)

    want = uuid.uuid4().hex
    ciphered = subject.protect(want)
    assert ciphered != want

    got = subject.unprotect(ciphered)
    assert got == want
