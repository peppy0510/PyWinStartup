# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import ctypes
import operator
import os
import psutil
import sys
import time
import win32api
import win32con
import win32gui
import win32process
import wx

from nateon import NateOn
from presets import PRESETS
from win32com.client import Dispatch


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def kill_existing_instances():
    pid = int(os.getpid())
    cwd = os.path.split(__file__)[0]
    for p in psutil.process_iter():
        try:
            p.cwd()
        except Exception:
            continue
        if p.pid != pid and p.cwd() == cwd and p.name().lower() in ('python.exe', 'pythonw.exe',):
            # only SIGTERM, CTRL_C_EVENT, CTRL_BREAK_EVENT signals on Windows Platform.
            # p.send_signal(signal.SIGTERM)
            p.terminate()


def run_as_admin(callback, file, try_run_as_admin=True):
    if try_run_as_admin is False or is_admin():
        callback()
    else:
        # Rerun with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, file, None, 1)


def create_shortcut(path, target_path='', arguments='', working_directory='', icon=''):
    ext = os.path.splitext(path)[-1][1:].lower()
    if ext == 'url':
        with open(path, 'w') as file:
            file.write('[InternetShortcut]\nURL=%s' % target_path)
    else:
        shell = Dispatch('WScript.Shell')

        shortcut = shell.CreateShortCut(
            path if path.endswith('.lnk') else '.'.join([path, 'lnk']))
        # shortcut.WindowStyle = 1
        shortcut.Arguments = arguments
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = working_directory
        if icon:
            shortcut.IconLocation = icon
        shortcut.save()
    print('[ SHORTCUT CREATED ] [ %s ]' % path)


def create_desktop_ini(directory, icon_resource, folder_type='Generic'):
    with open(os.path.join(directory, 'desktop.ini'), 'w') as file:
        file.write('\n'.join([
            '[.ShellClassInfo]', 'IconResource=%s,0' % icon_resource,
            '[ViewState]', 'Mode=', 'Vid=', 'FolderType=%s' % folder_type]))


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
        # PROCESS_QUERY_INFORMATION (0x0400) or PROCESS_VM_READ (0x0010) or PROCESS_ALL_ACCESS (0x1F0FFF)
        try:
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, self.pid)
            self.pname = win32process.GetModuleFileNameEx(process, 0).split(os.path.sep)[-1]
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
        self.presets = PRESETS
        self.parent = parent
        self.tic = time.time()
        self.interval = 1000
        self.maxuptime = 15
        self.nateon_patched = False
        self.Start(self.interval)

    def patch_nateon(self):
        nateon = NateOn()
        if not nateon.is_patched():
            nateon.run_patch()
        self.nateon_patched = True

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
                    print(str(window.pid).rjust(6), str(window.hwnd).rjust(8), str(window.parent).rjust(8),
                          window.visible, window.enabled, window.pname.ljust(24), window.title[:100])
                print('-' * 160)
        return windows

    def get_preset_action(self, window):
        for i in range(len(self.presets) - 1, -1, -1):
            pname = self.presets[i].get('pname')
            title = self.presets[i].get('title')
            if (pname is None or (pname is not None and pname == window.pname)) and\
                    (title is None or (title is not None and title == window.title)):
                return self.presets[i].get('action')

    def pop_preset(self, window):
        for i in range(len(self.presets) - 1, -1, -1):
            pname = self.presets[i].get('pname')
            title = self.presets[i].get('title')
            if (pname is None or (pname is not None and pname == window.pname)) and\
                    (title is None or (title is not None and title == window.title)):
                return self.presets.pop(i)

    def Notify(self):
        print(time.time() - self.tic)
        if len(self.presets) == 0 or time.time() - self.tic > self.maxuptime:
            self.Stop()
            self.parent.OnClose()

        for window in self.get_window_informations():
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

        self.patch_nateon()
