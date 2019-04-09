from msal.extensions._osx import Keychain
import uuid


def test_keychain_roundtrip():
    with Keychain() as subject:
        want = uuid.uuid4().hex
        subject.set_generic_password("msal_extension_test", "test_account", want)
        got = subject.get_generic_password("msal_extension_test", "test_account")
        assert got == want
