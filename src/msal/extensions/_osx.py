import os
import ctypes as _ctypes

OS_result = _ctypes.c_int32


class KeychainError(OSError):
    def __init__(self, exit_status):
        self.exit_status = exit_status
        # TODO: use SecCopyErrorMessageString to fetch the appropriate message here.
        self.message = '{} ' \
                       'check https://opensource.apple.com/source/CarbonHeaders/CarbonHeaders-18.1/MacErrors.h'.format(
                            self.exit_status)


class KeychainAccessDeniedError(KeychainError):
    EXIT_STATUS = -128

    def __init__(self):
        super().__init__(KeychainAccessDeniedError.EXIT_STATUS)


class NoSuchKeychainError(KeychainError):
    EXIT_STATUS = -25294

    def __init__(self, name):
        super().__init__(NoSuchKeychainError.EXIT_STATUS)
        self.name = name


class NoDefaultKeychainError(KeychainError):
    EXIT_STATUS = -25307

    def __init__(self):
        super().__init__(NoDefaultKeychainError.EXIT_STATUS)


class KeychainItemNotFoundError(KeychainError):
    @classmethod
    def exit_status(cls):
        return -25300

    def __init__(self, name):
        super().__init__(KeychainItemNotFoundError.exit_status())
        self.name = name


def _construct_error(exit_status, **kwargs):
    if exit_status == KeychainAccessDeniedError.EXIT_STATUS:
        return KeychainAccessDeniedError()
    if exit_status == NoSuchKeychainError.EXIT_STATUS:
        return NoSuchKeychainError(kwargs['keychain_name'])
    if exit_status == NoDefaultKeychainError.EXIT_STATUS:
        return NoDefaultKeychainError()
    if exit_status == KeychainItemNotFoundError.exit_status():
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
try:
    _security = _ctypes.CDLL(_get_native_location('Security'))
    _core = _ctypes.CDLL(_get_native_location('CoreFoundation'))
except OSError:
    _security = None
    _core = None

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


class Keychain(object):
    """Encapsulates the interactions with a particular MacOS Keychain."""
    def __init__(self, filename=None):
        # type: (str) -> None
        self._ref = _ctypes.c_void_p()

        if filename:
            filename = os.path.expanduser(filename)
            self._filename = filename.encode('utf-8')
        else:
            self._filename = None

    def __enter__(self):
        if self._filename:
            status = _securityKeychainOpen(self._filename, self._ref)
        else:
            status = _securityKeychainCopyDefault(self._ref)

        if not status:
            raise OSError(status)
        return self

    def __exit__(self, *args):
        if self._ref:
            _coreRelease(self._ref)

    def get_generic_password(self, service, account_name):
        # type: (str, str) -> str
        service = service.encode('utf-8')
        account_name = account_name.encode('utf-8')

        length = _ctypes.c_uint32()
        contents = _ctypes.c_void_p()
        exit_status = _securityKeychainFindGenericPassword(
            self._ref,
            len(service),
            service,
            len(account_name),
            account_name,
            length,
            contents,
            None,
        )

        if not exit_status:
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
            self._ref,
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
                self._ref,
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
        raise NotImplementedError()

    def set_internet_password(self, service, username, value):
        # type: (str, str, str) -> str
        raise NotImplementedError()

