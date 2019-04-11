# This code is modeled from a StackOverflow question, which can be found here:
# https://stackoverflow.com/questions/463832/using-dpapi-with-python

import ctypes

_local_free = ctypes.windll.kernel32.LocalFree
_memcpy = ctypes.cdll.msvcrt.memcpy
_crypt_protect_data = ctypes.windll.crypt32.CryptProtectData
_crypt_unprotect_data = ctypes.windll.crypt32.CryptUnprotectData
_CRYPTPROTECT_UI_FORBIDDEN = 0x01


class DATA_BLOB(ctypes.Structure):
    """
    A wrapper for interacting with the _CRYPTOAPI_BLOB type and its many aliases. This type is exposed from Wincrypt.h
    in XP and above.

    See documentation for this type at:
    https://msdn.microsoft.com/en-us/7a06eae5-96d8-4ece-98cb-cf0710d2ddbd
    """
    _fields_ = [("cbData", ctypes.wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    def raw(self):
        # type: () -> bytes
        cb_data = int(self.cbData)
        pb_data = self.pbData
        buffer = ctypes.c_buffer(cb_data)
        _memcpy(buffer, pb_data, cb_data)
        _local_free(pb_data)
        return buffer.raw


class WindowsDataProtectionAgent(object):
    def __init__(self, **kwargs):
        # type: (str) -> None
        if 'entropy' in kwargs:
            entropy = kwargs['entropy'].encode('utf-8')
            self._entropy_buffer = ctypes.c_buffer(entropy, len(entropy))
            self._entropy_blob = DATA_BLOB(len(entropy), self._entropy_buffer)
        else:
            self._entropy_buffer = None
            self._entropy_blob = None

    def protect(self, message):
        # type: (str) -> bytes

        message = message.encode('utf-8')
        message_buffer = ctypes.c_buffer(message, len(message))
        message_blob = DATA_BLOB(len(message), message_buffer)
        result = DATA_BLOB()

        if self._entropy_blob:
            entropy = ctypes.byref(self._entropy_blob)
        else:
            entropy = None

        if _crypt_protect_data(
                ctypes.byref(message_blob),
                u"python_data",
                entropy,
                None,
                None,
                _CRYPTPROTECT_UI_FORBIDDEN,
                ctypes.byref(result)):
            return result.raw()
        return b''

    def unprotect(self, cipher_text):
        # type: (bytes) -> str
        ct_buffer = ctypes.c_buffer(cipher_text, len(cipher_text))
        ct_blob = DATA_BLOB(len(cipher_text), ct_buffer)
        result = DATA_BLOB()

        if self._entropy_blob:
            entropy = ctypes.byref(self._entropy_blob)
        else:
            entropy = None

        if _crypt_unprotect_data(
            ctypes.byref(ct_blob),
            None,
            entropy,
            None,
            None,
            _CRYPTPROTECT_UI_FORBIDDEN,
            ctypes.byref(result)
        ):
            return result.raw().decode('utf-8')
        return u''
