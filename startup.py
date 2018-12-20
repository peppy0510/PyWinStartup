# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import operator
import os
import psutil
import pystray
import signal
import time
import win32api
import win32con
import win32gui
import win32process

from PIL import Image
from nateon import NateOn


POPUP_PRESET = [{
    'target': {
        'pname': 'KakaoTalk.exe',
        'title': '카카오톡'
    }, 'action': 'hide'
}, {
    'target': {
        'pname': 'WMOne.exe',
        'title': 'WMOne'
    }, 'action': 'hide'
}, {
    'target': {
        'pname': 'WMOne.exe',
        'title': 'LINE WORKS'
    }, 'action': 'hide'
}, {
    'target': {
        'pname': 'NateOnMain.exe',
        'title': 'NateOn'
    }, 'action': 'hide'
}, {
    'target': {
        'pname': 'NateOnMain.exe',
        'title': '네이트온 안내'
    }, 'action': 'hide'
}, {
    'target': {
        'pname': 'uTorrent.exe',
        'title': 'μTorrentPro'
    }, 'action': 'hide'
}]


KILLPROC_PRESET = [{
    'pname': 'acrotray.exe'
}, {
    'pname': 'HancomStudio.exe'
}, {
    'pname': 'HancomStudio_AD.exe'
}, {
    'pname': 'HncUpdateService.exe'
}, {
    'pname': 'SkypeBridge.exe'
}]


class WindowInformation():

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.title = win32gui.GetWindowText(self.hwnd)
        _, self.pid = win32process.GetWindowThreadProcessId(hwnd)
        self.visible = win32gui.IsWindowVisible(hwnd)
        self.enabled = win32gui.IsWindowEnabled(hwnd)
        # PROCESS_QUERY_INFORMATION (0x0400) or PROCESS_VM_READ (0x0010) or PROCESS_ALL_ACCESS (0x1F0FFF)
        try:
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, self.pid)
            self.pname = win32process.GetModuleFileNameEx(process, 0).split(os.path.sep)[-1]
        except Exception:
            self.pname = ''

        try:
            self.parent = win32gui.GetParent(hwnd)
        except Exception:
            pass

    def close(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)

    def hide(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def minimize(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)


class ProcInformation():

    def __init__(self, proc):
        self.pid = proc.pid
        self.pname = proc.name()

    def kill(self):
        try:
            os.kill(self.pid, signal.SIGINT)
        except Exception:
            pass


class StartUpManager():

    def __init__(self):
        self.interval = 0.5
        self.maxuptime = 30
        self.windows = []
        self.is_nateon_patched = False
        self.startuptime = time.time()

    @property
    def is_finished(self):
        if not self.is_nateon_patched:
            return False
        for preset in POPUP_PRESET:
            if preset.get('done'):
                return False
        for preset in KILLPROC_PRESET:
            if preset.get('done'):
                return False
        return True

    def nateon_patch_handler(self):
        nateon = NateOn()
        if not nateon.is_patched():
            nateon.run_patch()
        self.is_nateon_patched = True

    def close_popup_handler(self):
        for preset in POPUP_PRESET:
            if preset.get('done'):
                continue
            action = preset.get('action')
            title = preset['target'].get('title')
            pname = preset['target'].get('pname')
            for window in self.windows:
                if (pname is None or (pname is not None and pname == window.pname)) \
                        and (title is None or (title is not None and title == window.title)):
                    # print(preset.get('action'), window.pname, window.title)
                    if action == 'close':
                        getattr(window, action)()
                    if action in ('hide', 'minimize',) and window.visible:
                        getattr(window, action)()
                    preset['done'] = True

    def kill_proc_handler(self):
        for preset in KILLPROC_PRESET:
            if preset.get('done'):
                continue
            pname = preset.get('pname')
            for proc in self.procs:
                if pname == proc.pname:
                    # print(proc.pname)
                    proc.kill()
                preset['done'] = True

    def get_window_informations(self):

        def callback(hwnd, windows):
            window = WindowInformation(hwnd)
            excludes = ('Default IME', 'MSCTFIME UI', 'G',)
            if window.pname and window.title and window.title not in excludes:
                windows += [window]

        windows = []
        win32gui.EnumWindows(callback, windows)
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

    def get_proc_informations(self):
        procs = []
        excludes = ('conhost.exe', 'svchost.exe', 'RuntimeBroker.exe',)
        for proc in psutil.process_iter():
            if proc.name() not in excludes:
                procs += [ProcInformation(proc)]
        procs = sorted(procs, key=operator.attrgetter('pname'))
        if True:
            if not hasattr(self, '__procs_logged__') or not self.__procs_logged__:
                self.__procs_logged__ = True
                print('-' * 160)
                for proc in procs:
                    print(proc.pid, proc.pname)
                print('-' * 160)
        return procs

    def handle_existing_instances(self):
        pid = os.getpid()
        cwd = os.path.split(__file__)[0]
        processes = []
        for p in psutil.process_iter():
            try:
                p.cwd()
            except Exception:
                continue
            processes += [{'pid': p.pid, 'cwd': p.cwd(), 'name': p.name()}]
        processes = sorted(processes, key=operator.itemgetter('cwd'))

        if False:
            print('-' * 120)
            for p in processes:
                print(str(p['pid']).rjust(6), p['cwd'].ljust(64), p['name'].ljust(6))
            print('-' * 120)
            print(str(pid).rjust(6))
            print('-' * 120)

        for p in processes:
            if p['pid'] != pid and p['cwd'] == cwd and p['name'] in ('python.exe', 'pythonw.exe',):
                os.kill(p['pid'], signal.SIGINT)

    def run(self):
        self.handle_existing_instances()
        while not self.is_finished and time.time() - self.startuptime < self.maxuptime:
            time.sleep(self.interval)
            self.procs = self.get_proc_informations()
            self.windows = self.get_window_informations()
            self.kill_proc_handler()
            self.close_popup_handler()
            self.nateon_patch_handler()
        stop()


def stop():
    icon.visible = False
    icon.stop()
    pid = os.getpid()
    os.kill(pid, signal.SIGINT)


trayicon = Image.open('icon.png')
icon = pystray.Icon('STARTUP', trayicon, 'STARTUP')
icon.menu = pystray.Menu(
    pystray.MenuItem('STARTUP 0.0.1', lambda item: None),
    pystray.MenuItem('author: Taehong Kim', lambda item: None),
    pystray.MenuItem('email: peppy0510@hotmail.com', lambda item: None),
    pystray.MenuItem('Quit STARTMAN', stop, checked=lambda item: True),
)
icon.visible = True


def startup_manager(event):
    manager = StartUpManager()
    manager.run()


def main():
    '''
    ABOVE_NORMAL_PRIORITY_CLASS
    BELOW_NORMAL_PRIORITY_CLASS
    HIGH_PRIORITY_CLASS
    IDLE_PRIORITY_CLASS
    NORMAL_PRIORITY_CLASS
    REALTIME_PRIORITY_CLASS
    '''
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    icon.run(startup_manager)


if __name__ == '__main__':
    main()
