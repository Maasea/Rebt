# -----------------------------------------------------------------------------
#  Copyright (C) 2019 Alberto Sottile
#
#  Distributed under the terms of the 3-clause BSD License.
# -----------------------------------------------------------------------------
import sys
import platform
from winreg import HKEY_CURRENT_USER as hkey, QueryValueEx as getSubkeyValue, OpenKey as getKey
import ctypes
import ctypes.wintypes

advapi32 = ctypes.windll.advapi32
advapi32.RegOpenKeyExA.argtypes = (
    ctypes.wintypes.HKEY,
    ctypes.wintypes.LPCSTR,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.POINTER(ctypes.wintypes.HKEY),
)
advapi32.RegOpenKeyExA.restype = ctypes.wintypes.LONG
advapi32.RegQueryValueExA.argtypes = (
    ctypes.wintypes.HKEY,
    ctypes.wintypes.LPCSTR,
    ctypes.wintypes.LPDWORD,
    ctypes.wintypes.LPDWORD,
    ctypes.wintypes.LPBYTE,
    ctypes.wintypes.LPDWORD,
)
advapi32.RegQueryValueExA.restype = ctypes.wintypes.LONG
advapi32.RegNotifyChangeKeyValue.argtypes = (
    ctypes.wintypes.HKEY,
    ctypes.wintypes.BOOL,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.BOOL,
)
advapi32.RegNotifyChangeKeyValue.restype = ctypes.wintypes.LONG

hKey = ctypes.wintypes.HKEY()
advapi32.RegOpenKeyExA(
    ctypes.wintypes.HKEY(0x80000001),  # HKEY_CURRENT_USER
    ctypes.wintypes.LPCSTR(b'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'),
    ctypes.wintypes.DWORD(),
    ctypes.wintypes.DWORD(0x00020019),  # KEY_READ
    ctypes.byref(hKey),
)
dwSize = ctypes.wintypes.DWORD(ctypes.sizeof(ctypes.wintypes.DWORD))
queryValueLast = ctypes.wintypes.DWORD()
queryValue = ctypes.wintypes.DWORD()
advapi32.RegQueryValueExA(
    hKey,
    ctypes.wintypes.LPCSTR(b'AppsUseLightTheme'),
    ctypes.wintypes.LPDWORD(),
    ctypes.wintypes.LPDWORD(),
    ctypes.cast(ctypes.byref(queryValueLast), ctypes.wintypes.LPBYTE),
    ctypes.byref(dwSize),
)


class DarkMode:
    def __init__(self):
        self.should_stop = False
        self._setup_system_dependent()

    def _setup_system_dependent(self):
        if sys.platform == "win32" and platform.release().isdigit() and int(platform.release()) >= 10:
            winver = int(platform.version().split('.')[2])

            self._is_capable = winver >= 14393

        else:
            self._is_capable = False

    def theme(self):
        if self._is_capable:
            valueMeaning = {0: "Dark", 1: "Light"}
            try:
                key = getKey(hkey, "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
                subkey = getSubkeyValue(key, "AppsUseLightTheme")[0]
            except FileNotFoundError:
                return None
            return valueMeaning[subkey]
        else:
            return None

    def isDark(self):
        return self.theme() == 'Dark' if self._is_capable else None

    def isLight(self):
        return self.theme() == 'Light' if self._is_capable else None

    def listener(self, callback):
        if not self._is_capable:
            raise NotImplementedError()

        while not self.should_stop:
            advapi32.RegNotifyChangeKeyValue(
                hKey,
                ctypes.wintypes.BOOL(True),
                ctypes.wintypes.DWORD(0x00000004),  # REG_NOTIFY_CHANGE_LAST_SET
                ctypes.wintypes.HANDLE(None),
                ctypes.wintypes.BOOL(False),
            )
            advapi32.RegQueryValueExA(
                hKey,
                ctypes.wintypes.LPCSTR(b'AppsUseLightTheme'),
                ctypes.wintypes.LPDWORD(),
                ctypes.wintypes.LPDWORD(),
                ctypes.cast(ctypes.byref(queryValue), ctypes.wintypes.LPBYTE),
                ctypes.byref(dwSize),
            )
            if queryValueLast.value != queryValue.value:
                queryValueLast.value = queryValue.value
                callback('Light' if queryValue.value else 'Dark')

    def stop(self):
        self.should_stop = True
        result = advapi32.RegCloseKey(hKey)
        if result != 0:
            print(f'Failed to close key: {result}')
