from msal.extensions._windows import WindowsDataProtectionAgent
import uuid


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
