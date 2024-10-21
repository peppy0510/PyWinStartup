# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import operator
import os
import psutil
import time
import win32api
import win32con
import win32gui
import win32process
import wx

from .kakaotalk import KakaoTalk
from .nateon import NateOn
from .powershell import PowerShell
from presets import INTERVAL
from presets import PATCH
from presets import PRESETS
from presets import UPTIME


class WindowInformation():

    def __init__(self, hwnd=None, pid=None):
        self.pid = pid
        self.hwnd = hwnd
        if hwnd is not None:
            self.title = win32gui.GetWindowText(hwnd)
            _, self.pid = win32process.GetWindowThreadProcessId(hwnd)
            self.visible = win32gui.IsWindowVisible(hwnd)
            self.enabled = win32gui.IsWindowEnabled(hwnd)
        else:
            self.title = ''
            self.visible = None
            self.enabled = None

        if pid is not None:
            try:
                p = psutil.Process(pid)
                self.pname = p.name()
            except Exception:
                pass
            # print(self.pname)
        # (PROCESS_QUERY_INFORMATION(0x0400) or
        #     PROCESS_VM_READ(0x0010) or PROCESS_ALL_ACCESS(0x1F0FFF))
        try:
            process = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION, False, self.pid)
            self.pname = win32process.GetModuleFileNameEx(
                process, 0).split(os.path.sep)[-1]
        except Exception:
            self.pname = ''

        try:
            self.parent = win32gui.GetParent(hwnd)
        except Exception:
            self.parent = None

    def kill(self):
        p = psutil.Process(self.pid)
        p.terminate()

    def close(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)

    def hide(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def minimize(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)


class StartUpWatcher(wx.Timer):

    def __init__(self, parent):
        super(wx.Timer, self).__init__()
        self.presets = [v for v in PRESETS if v.get('action') in ('hide', 'kill',)]
        self.parent = parent
        self.tic = time.time()
        self.interval = INTERVAL * 1000
        self.maxuptime = UPTIME
        self.nateon_patched = False
        self.kakaotalk_patched = False
        self.powershell_patched = False
        self.Start(self.interval)
        self.kakaotalk = KakaoTalk()
        self.powershell = PowerShell()

    def patch_kakaotalk(self):
        if not PATCH.get('KAKAOTALK'):
            return
        if not self.kakaotalk.patched:
            self.kakaotalk.run_patch()

    def patch_nateon(self):
        if not PATCH.get('NATEON'):
            return
        nateon = NateOn()
        if not nateon.is_patched():
            nateon.run_patch()
        self.nateon_patched = True

    def patch_powershell(self):
        if not PATCH.get('POWERSHELL'):
            return
        if not self.powershell.patched:
            self.powershell.run_patch()

    def get_window_informations(self):

        if not hasattr(self, 'checked_pids'):
            self.checked_pids = []

        if not hasattr(self, 'psutil_proxy'):
            self.psutil_proxy = []

        def callback(hwnd, windows):
            window = WindowInformation(hwnd=hwnd)
            excludes = ('Default IME', 'MSCTFIME UI', 'G',)
            if window.pname and window.title and window.title not in excludes:
                windows += [window]

        windows = []
        win32gui.EnumWindows(callback, windows)
        window_pids = [v.pid for v in windows]

        for pid in psutil.pids():
            if pid in self.checked_pids or pid in window_pids:
                continue
            windows += [WindowInformation(pid=pid)]

        windows = sorted(windows, key=operator.attrgetter('pid', 'hwnd'))

        if False:
            if not hasattr(self, '__windows_logged__') or not self.__windows_logged__:
                self.__windows_logged__ = True
                print('-' * 160)
                for window in windows:
                    print(str(window.pid).rjust(6),
                          str(window.hwnd).rjust(8),
                          str(window.parent).rjust(8),
                          window.visible, window.enabled,
                          window.pname.ljust(24), window.title[:100])
                print('-' * 160)
        return windows

    def get_preset_action(self, window):
        for i in range(len(self.presets) - 1, -1, -1):
            pname = self.presets[i].get('pname')
            title = self.presets[i].get('title')
            if (pname is None or (pname is not None and pname == window.pname)) and\
                    (not title or (title and title == window.title)):
                return self.presets[i].get('action')

    def pop_preset(self, window):
        for i in range(len(self.presets) - 1, -1, -1):
            pname = self.presets[i].get('pname')
            title = self.presets[i].get('title')
            if (pname is None or (pname is not None and pname == window.pname)) and\
                    (not title or (title and title == window.title)):
                return self.presets.pop(i)

    def Notify(self):
        self.patch_powershell()
        # print(f'{time.time() - self.tic:07.03f}')
        if len(self.presets) == 0 or time.time() - self.tic > self.maxuptime:
            self.Stop()
            self.parent.OnClose()

        for window in self.get_window_informations():
            # if 'Swit' in window.pname:
            #     # print(window.pname)
            #     window.hide()
            action = self.get_preset_action(window)
            if action == 'hide' and window.visible:
                self.pop_preset(window)
                window.hide()
            elif action == 'minimize' and window.visible:
                self.pop_preset(window)
                window.minimize()
            elif action == 'close':
                self.pop_preset(window)
                window.close()
            elif action == 'kill':
                self.pop_preset(window)
                window.kill()
            if window.pname == 'KakaoTalk.exe' and window.enabled:
                self.patch_kakaotalk()

        self.patch_nateon()
