import ctypes as _ctypes
import os

OS_result = _ctypes.c_int32


class KeychainError(OSError):
    def __init__(self, exit_status):
        self.exit_status = exit_status
        # TODO: use SecCopyErrorMessageString to fetch the appropriate message here.
        self.message = '{} ' \
                       'check https://opensource.apple.com/source/CarbonHeaders/CarbonHeaders-18.1/MacErrors.h'.format(
                            self.exit_status)


class KeychainAccessDeniedError(KeychainError):
    @classmethod
    def exit_status(cls):
        return -128

    def __init__(self):
        super().__init__(KeychainAccessDeniedError.exit_status())


class NoSuchKeychainError(KeychainError):
    @classmethod
    def exit_status(cls):
        return -25294

    def __init__(self, name):
        super().__init__(NoSuchKeychainError.exit_status())
        self.name = name


class NoDefaultKeychainError(KeychainError):
    @classmethod
    def exit_status(cls):
        return -25307

    def __init__(self):
        super().__init__(NoDefaultKeychainError.exit_status())


class KeychainItemNotFoundError(KeychainError):
    @classmethod
    def exit_status(cls):
        return -25300

    def __init__(self, name):
        super().__init__(KeychainItemNotFoundError.exit_status())
        self.name = name


def _construct_error(**kwargs):
    if kwargs['exit_status'] == KeychainAccessDeniedError.exit_status():
        return KeychainAccessDeniedError()
    if kwargs['exit_status'] == NoSuchKeychainError.exit_status():
        return NoSuchKeychainError(kwargs['keychain_name'])
    if kwargs['exit_status'] == NoDefaultKeychainError.exit_status():
        return NoDefaultKeychainError()
    if kwargs['exit_status'] == KeychainItemNotFoundError.exit_status():
        return KeychainItemNotFoundError(kwargs['item_name'])


def _get_native_location(name):
    # type: (str) -> str
    """
    Fetches the location of a native MacOS library.
    :param name: The name of the library to be loaded.
    :return: The location of the library on a MacOS filesystem.
    """
    return '/System/Library/Frameworks/{0}.framework/{0}'.format(name)


# Load native MacOS libraries
_security = _ctypes.CDLL(_get_native_location('Security'))
_core = _ctypes.CDLL(_get_native_location('CoreFoundation'))

# Bind CFRelease from native MacOS libraries.
_coreRelease = _core.CFRelease
_coreRelease.argtypes = (
    _ctypes.c_void_p,
)

# Bind SecCopyErrorMessageString from native MacOS libraries.
# https://developer.apple.com/documentation/security/1394686-seccopyerrormessagestring?language=objc
_securityCopyErrorMessageString = _security.SecCopyErrorMessageString
_securityCopyErrorMessageString.argtypes = (
    OS_result,
    _ctypes.c_void_p
)
_securityCopyErrorMessageString.restype = _ctypes.c_char_p

# Bind SecKeychainOpen from native MacOS libraries.
# https://developer.apple.com/documentation/security/1396431-seckeychainopen
_securityKeychainOpen = _security.SecKeychainOpen
_securityKeychainOpen.argtypes = (
    _ctypes.c_char_p,
    _ctypes.POINTER(_ctypes.c_void_p)
)
_securityKeychainOpen.restype = OS_result

# Bind SecKeychainCopyDefault from native MacOS libraries.
# https://developer.apple.com/documentation/security/1400743-seckeychaincopydefault?language=objc
_securityKeychainCopyDefault = _security.SecKeychainCopyDefault
_securityKeychainCopyDefault.argtypes = (
    _ctypes.POINTER(_ctypes.c_void_p),
)
_securityKeychainCopyDefault.restype = OS_result


# Bind SecKeychainItemFreeContent from native MacOS libraries.
_securityKeychainItemFreeContent = _security.SecKeychainItemFreeContent
_securityKeychainItemFreeContent.argtypes = (
    _ctypes.c_void_p,
    _ctypes.c_void_p,
)
_securityKeychainItemFreeContent.restype = OS_result

# Bind SecKeychainItemModifyAttributesAndData from native MacOS libraries.
_securityKeychainItemModifyAttributesAndData = _security.SecKeychainItemModifyAttributesAndData
_securityKeychainItemModifyAttributesAndData.argtypes = (
    _ctypes.c_void_p,
    _ctypes.c_void_p,
    _ctypes.c_uint32,
    _ctypes.c_void_p,
)
_securityKeychainItemModifyAttributesAndData.restype = OS_result

# Bind SecKeychainFindGenericPassword from native MacOS libraries.
# https://developer.apple.com/documentation/security/1397301-seckeychainfindgenericpassword?language=objc
_securityKeychainFindGenericPassword = _security.SecKeychainFindGenericPassword
_securityKeychainFindGenericPassword.argtypes = (
    _ctypes.c_void_p,
    _ctypes.c_uint32,
    _ctypes.c_char_p,
    _ctypes.c_uint32,
    _ctypes.c_char_p,
    _ctypes.POINTER(_ctypes.c_uint32),
    _ctypes.POINTER(_ctypes.c_void_p),
    _ctypes.POINTER(_ctypes.c_void_p),
)
_securityKeychainFindGenericPassword.restype = OS_result

# Bind SecKeychainAddGenericPassword from native MacOS
# https://developer.apple.com/documentation/security/1398366-seckeychainaddgenericpassword?language=objc
_securityKeychainAddGenericPassword = _security.SecKeychainAddGenericPassword
_securityKeychainAddGenericPassword.argtypes = (
    _ctypes.c_void_p,
    _ctypes.c_uint32,
    _ctypes.c_char_p,
    _ctypes.c_uint32,
    _ctypes.c_char_p,
    _ctypes.c_uint32,
    _ctypes.c_char_p,
    _ctypes.POINTER(_ctypes.c_void_p),
)
_securityKeychainAddGenericPassword.restype = OS_result


class Keychain:
    """Encapsulates the interactions with a particular MacOS Keychain"""
    def __init__(self, filename=None):
        # type: (str) -> None
        self.ref = _ctypes.c_void_p()

        if filename:
            filename = os.path.expanduser(filename)
            self.filename = filename.encode('utf-8')
        else:
            self.filename = None

    def __enter__(self):
        if self.filename:
            status = _securityKeychainOpen(self.filename, self.ref)
        else:
            status = _securityKeychainCopyDefault(self.ref)

        if status != 0:
            raise OSError(status)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ref:
            _coreRelease(self.ref)

    def get_generic_password(self, service, account_name):
        # type: (str, str) -> str
        service = service.encode('utf-8')
        account_name = account_name.encode('utf-8')

        length = _ctypes.c_uint32()
        contents = _ctypes.c_void_p()
        exit_status = _securityKeychainFindGenericPassword(
            self.ref,
            len(service),
            service,
            len(account_name),
            account_name,
            length,
            contents,
            None,
        )

        if exit_status != 0:
            raise _construct_error(exit_status=exit_status)

        value = _ctypes.create_string_buffer(length.value)
        _ctypes.memmove(value, contents.value, length.value)
        _securityKeychainItemFreeContent(None, contents)
        return value.raw.decode('utf-8')

    def set_generic_password(self, service, account_name, value):
        # type: (str, str, str) -> None
        service = service.encode('utf-8')
        account_name = account_name.encode('utf-8')
        value = value.encode('utf-8')
        entry = _ctypes.c_void_p()
        find_exit_status = _securityKeychainFindGenericPassword(
            self.ref,
            len(service),
            service,
            len(account_name),
            account_name,
            None,
            None,
            entry,
        )

        if find_exit_status == 0:
            modify_exit_status = _securityKeychainItemModifyAttributesAndData(
                entry,
                None,
                len(value),
                value,
            )
            _securityKeychainItemFreeContent(None, entry)
        elif find_exit_status == KeychainItemNotFoundError.exit_status():
            add_exit_status = _securityKeychainAddGenericPassword(
                self.ref,
                len(service),
                service,
                len(account_name),
                account_name,
                len(value),
                value,
                None
            )

            if add_exit_status != 0:
                raise OSError(add_exit_status)
        else:
            raise OSError(find_exit_status)

    def get_internet_password(self, service, username):
        # type: (str, str) -> str
        raise NotImplementedError

    def set_internet_password(self, service, username, value):
        # type: (str, str, str) -> str
        raise NotImplementedError
