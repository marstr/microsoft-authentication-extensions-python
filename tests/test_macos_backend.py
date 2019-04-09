from msal.extensions._osx import Keychain
import uuid


def test_keychain_roundtrip():
    with Keychain() as subject:
        location, account = "msal_extension_test1", "test_account1"
        want = uuid.uuid4().hex
        subject.set_generic_password(location, account, want)
        got = subject.get_generic_password(location, account)
        assert got == want

