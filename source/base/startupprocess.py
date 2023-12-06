# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import operator
import os
import psutil
import shlex
import subprocess
import time
import win32api
import win32con
import win32gui
import win32process
import wx

from .startupwatcher import StartUpWatcher
from pathlib import Path
from presets import INTERVAL
from presets import PRESETS
from presets import UPTIME


class StartUpProcess(wx.Timer):

    def __init__(self, parent):
        super(wx.Timer, self).__init__()
        self.presets = [v for v in PRESETS if v.get('action') in ('start',)]
        self.parent = parent
        self.tic = time.time()
        self.interval = INTERVAL * 1000
        self.maxuptime = UPTIME
        self.pending = False
        self.Start(self.interval)

    def Notify(self):
        if self.pending:
            return
        self.pending = True
        self.resolve_procs()
        for preset in self.presets:
            self.process_preset(preset)

    def resolve_procs(self):
        self.procs = []
        for proc in psutil.process_iter():
            try:
                cmdline = proc.cmdline()
                if len(cmdline) > 2 and cmdline[1] == 'PackagedDataInfo:':
                    cmdline = cmdline[2:]
                self.procs += [dict(
                    pid=proc.pid,
                    cwd=proc.cwd(), name=proc.name(), cmdline=cmdline,
                )]
            except Exception:
                pass

    def get_pid(self, cmd, renew=False):
        if not renew:
            for v in self.procs:
                if v.get('cmdline') == cmd:
                    return v.get('pid')
            return

        for proc in psutil.process_iter():
            try:
                cmdline = proc.cmdline()
                if len(cmdline) > 2 and cmdline[1] == 'PackagedDataInfo:':
                    cmdline = cmdline[2:]
                if cmdline == cmd:
                    return proc.pid
            except Exception:
                pass

    # def get_windows(self):
    #     windows = []

    #     def window_enumeration_handler(hwnd, top_windows):
    #         windows.append((hwnd, win32gui.GetWindowText(hwnd),))

    #     win32gui.EnumWindows(window_enumeration_handler, windows)

    #     return windows
    #     for hwnd, title in windows:
    #         print(hwnd, title)

    def get_hwnd(self, pid):
        proc = psutil.Process(pid)
        # parents = proc.parents()
        # children = proc.children()
        # print(dir(proc))
        # print(parents)
        # print(children)
        # print(pid, dir(proc))
        # print(proc.cmdline())
        # print(proc.username())
        hwnds = []
        win32gui.EnumWindows(lambda v, vv: vv.append(v), hwnds)
        for hwnd in hwnds:
            # print(win32process.GetWindowThreadProcessId(hwnd))
            for _ in range(50):
                # title = win32gui.GetWindowText(hwnd)
                _tid, _pid = win32process.GetWindowThreadProcessId(hwnd)
                # if 'TimeKit' in title:
                #     proc = psutil.Process(_pid)
                #     print(title, _tid, _pid, pid, [v.pid for v in proc.parents()[0].children()])
                if _pid == pid:
                    return hwnd
                try:
                    hwnd = win32gui.GetParent(hwnd)
                except Exception:
                    break

    def set_position(self, pid, x, y, width, height, repaint=True):
        # hwnd = pid
        # hwnd = win32gui.GetParent(hwnd)
        hwnd = self.get_hwnd(pid)
        print(hwnd)
        if not hwnd:
            return
        # pid = win32process.GetWindowThreadProcessId(hwnd)
        # try:
        #     process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, self.pid)
        #     self.pname = win32process.GetModuleFileNameEx(process, 0).split(os.path.sep)[-1]
        # except Exception:
        #     self.pname = ''

        # try:
        #     self.parent = win32gui.GetParent(hwnd)
        # except Exception:
        #     self.error = True
        # parent = win32gui.GetParent(hwnd)
        # print(parent)
        # if parent:
        #     hwnd = parent
        # 720 * 837
        # hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
        win32gui.MoveWindow(hwnd, x, y, width, height, repaint)

        # try:
        #     win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
        #     win32gui.MoveWindow(hwnd, x, y, width, height, repaint)
        #     return True
        # except Exception:
        #     print('Admin rights required.')
        # return False

    def process_preset(self, preset):
        pos = preset.get('pos')
        cmd = preset.get('popen')

        if not cmd:
            return
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        pid = self.get_pid(cmd)
        if pid:
            print('[popen already exists]', pid, shlex.join(cmd))
        else:
            cwd = preset.get('cwd') or None
            subprocess.Popen(*cmd, cwd=cwd, close_fds=True, start_new_session=True)
            pid = self.get_pid(cmd, True)
            print('[popen start]', pid, shlex.join(cmd))
        # if pos:
        #     self.set_position(pid, *pos)
