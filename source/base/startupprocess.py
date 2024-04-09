# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import asyncio
import operator
import os
import psutil
import random
import re
import shlex
import string
import subprocess
import time
import win32api
import win32con
import win32gui
import win32process
import wx

from .startupwatcher import StartUpWatcher
from operator import itemgetter
from pathlib import Path
from presets import INTERVAL
from presets import PRESETS
from presets import UPTIME


class StartUpProcess(wx.Timer):

    def __init__(self, parent):
        super(wx.Timer, self).__init__()
        self.presets = [v for v in PRESETS if v.get('action') in ('start',)]
        [v.update(after=0) for v in self.presets if not v.get('after')]
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
        # time.sleep(30)
        # self.resolve_procs()
        for preset in sorted(self.presets, key=itemgetter('after')):
            self.process_preset(preset)

    # def resolve_procs(self):
    #     self.procs = []
    #     for proc in psutil.process_iter():
    #         try:
    #             cmdline = proc.cmdline()
    #             if len(cmdline) > 2 and cmdline[1] == 'PackagedDataInfo:':
    #                 cmdline = cmdline[2:]
    #             if 'WindowsApps\\Microsoft.WindowsTerminal' in cmdline[0]:
    #                 cmdline[0] = 'WindowsApps\\Microsoft.WindowsTerminal'
    #             self.procs += [dict(
    #                 pid=proc.pid, cwd=proc.cwd(),
    #                 name=proc.name(), cmdline=cmdline,
    #             )]
    #         except Exception:
    #             pass
    def trim_cmd(self, cmd):
        for i in range(len(cmd)):
            pattern = r'^[a-zA-Z]:\\.*\\WindowsApps\\Microsoft\.WindowsTerminal.*\\wt\.exe$'
            if re.match(pattern, cmd[i]):
                cmd[i] = 'wt.exe'
        return cmd

    def get_proc_pid_cmd_cwds(self, proc):
        responses = []
        for i in range(1):
            try:
                pid = proc.pid
                # cwd = proc.cwd()
                cmd = proc.cmdline()
                # identifier = proc.environ().get('PYWINSTARTUP_IDENTIFIER')
                # print(dir(proc))
                # print(cmd)
                cmd = self.trim_cmd(cmd)
                cmd = ' '.join(cmd)
                # cmd = shlex.split(cmd)
                # for i in range(len(cmd)):
                #     if cmd[i].startswith('"') and cmd[i].endswith('"'):
                #         cmd[i] = cmd[i].strip('"')
                # cmd = ' '.join(cmd)
                # responses += [(pid, cmd, cwd, identifier)]
                # responses += [(pid, cmd, cwd)]
                responses += [(pid, cmd)]
                # responses += [(pid, cmdline, cwd,)]
            except Exception:
                break
            try:
                proc = proc.parent()
            except Exception:
                break
        return responses

    def get_pid(self, cmd, cwd=None, identifier=None, renew=False):

        # for i in range(len(cmd)):
        #     pattern = r'^[a-zA-Z]:\\.*\\WindowsApps\\Microsoft\.WindowsTerminal.*\\wt\.exe$'
        #     if re.match(pattern, cmd[i]):
        #         cmd[i] = 'wt.exe'

        cmd = self.trim_cmd(cmd)
        cmd = ' '.join(cmd)
        # cmd = shlex.split(cmd)
        # for i in range(len(cmd)):
        #     if cmd[i].startswith('"') and cmd[i].endswith('"'):
        #         cmd[i] = cmd[i].strip('"')
        # cmd = ' '.join(cmd)
        # cmd = shlex.split(cmd)

        # for i in range(len(cmd)):
        #     cmd[i] = cmd[i].strip('"')

        # if 'WindowsApps\\Microsoft.WindowsTerminal' in cmd[0]:
        #     cmd[0] = 'WindowsApps\\Microsoft.WindowsTerminal'

        # if not renew:
        #     for v in self.procs:
        #         if v.get('cmdline') == cmd:
        #             return v.get('pid')
        #         # if 'WindowsApps\\Microsoft.WindowsTerminalPreview' in v.get('cmdline'):
        #         #     cmdline[0] = 'WindowsApps\\Microsoft.WindowsTerminalPreview'
        #     return

        # pid_procs = []
        for proc in psutil.process_iter():
            responses = self.get_proc_pid_cmd_cwds(proc)
            # print(responses)
            for i in range(len(responses)):
                # _pid, _cmd, _cwd, _identifier = responses[i]
                _pid, _cmd = responses[i]
                if _cmd.endswith(cmd):
                    return _pid
                    # return [v[0] for v in responses[i:]]
                # if identifier and _identifier == identifier:
                #     return _pid
                # resps = responses[:i]
                # return responses[0][0] if resps else _pid
                # if [v for v in _cmd if 'Time' in v]:
                #     print(_cmd)

                # if cmd[:1] != _cmd[:1]:
                #     continue
                # # if (cmd != _cmd) or (cwd and _cwd != cwd):
                # #     continue
                # return _pid

            # try:
            #     cmdline = proc.cmdline()
            #     # print('cmdline', cmdline)
            #     if len(cmdline) > 2 and cmdline[1] == 'PackagedDataInfo:':
            #         cmdline = cmdline[2:]
            #     if 'WindowsApps\\Microsoft.WindowsTerminal' in cmdline[0]:
            #         cmdline[0] = 'WindowsApps\\Microsoft.WindowsTerminal'
            #     if cmdline == cmd:
            #         return proc.pid
            #     pid_procs += [dict(pid=proc.pid, cmdline=cmdline)]
            # except Exception:
            #     pass

        # if 'WindowsApps\\Microsoft.WindowsTerminal' in cmd[0]:
        #     _pid_procs = [v for v in pid_procs if (
        #         'WindowsApps\\Microsoft.WindowsTerminal') in v.get('cmdline')[0]]
        #     _pid_procs = sorted(_pid_procs, key=itemgetter('pid'))
        #     # print(_pid_procs[-2].get('cmdline'))
        #     # return _pid_procs[-2].get('pid') if _pid_procs else None

    # def get_windows(self):
    #     windows = []

    #     def window_enumeration_handler(hwnd, top_windows):
    #         windows.append((hwnd, win32gui.GetWindowText(hwnd),))

    #     win32gui.EnumWindows(window_enumeration_handler, windows)

    #     return windows
    #     for hwnd, title in windows:
    #         print(hwnd, title)

    # def get_identifier_pid(self, identifier):
    #     for proc in psutil.process_iter():
    #         try:
    #             # print(proc.name())

    #             print(proc.parent().parent().cwd())
    #             print(proc.parent().parent().cmdline())
    #             # _identifier = proc.parent().parent().environ().get('PYWINSTARTUP_IDENTIFIER')
    #             # print(proc.parent().environ())
    #             # print(dir(proc.parent()))
    #             # _identifier = proc.environ()
    #             # print(_identifier)
    #             # if _identifier:
    #             #     print(_identifier)
    #             # if _identifier == identifier:
    #             #     return proc.pid
    #         except Exception:
    #             pass

    def get_relative_pids(self, pid):
        if not pid:
            return
        pids = []
        proc = psutil.Process(pid)
        for _ in range(1):
            if not proc:
                continue
            pids += [proc.pid]
            # try:
            #     pids += [v.pid for v in proc.parents()]
            # except Exception:
            #     continue
            try:
                pids += [v.pid for v in proc.children()]
            except Exception:
                continue
            try:
                proc = proc.parent()
            except Exception:
                break

        pids = list(set(pids))
        return pids

    def get_hwnd(self, pid, title=None):
        pids = self.get_relative_pids(pid)
        if not pid:
            return

        # print(dir(win32gui))
        # print(dir(win32process))
        # parents = proc.parents()
        # children = proc.children()
        # print(dir(proc))
        # print(parents)
        # print(children)
        # print(pid, dir(proc))
        # print(proc.cmdline())
        # print(proc.username())
        hwnds = []
        # EnumProcesses
        win32gui.EnumWindows(lambda v, vv: vv.append(v), hwnds)

        # print(hwnds)
        _hwnds = []
        # for hwnd in hwnds[::-1]:
        for hwnd in hwnds:
            # GetStartupInfo
            # top_window = win32gui.GetTopWindow(hwnd)
            _tid, _pid = win32process.GetWindowThreadProcessId(hwnd)
            if _pid in pids:
                _hwnds += [hwnd]
                break
                # continue
                # return hwnd
            if title:
                _title = win32gui.GetWindowText(hwnd)
                if _title == title:
                    _hwnds += [hwnd]
                    break
                    # return hwnd

        return _hwnds
        return list(set(_hwnds))
        # try:
        #     top_window = win32gui.GetTopWindow(hwnd)
        # except Exception:
        #     continue
        # if not top_window:
        #     continue
        # _tid, _pid = win32process.GetWindowThreadProcessId(top_window)
        # if _pid in pids:
        #     return top_window

        # for _ in range(50):
        # title = win32gui.GetWindowText(hwnd)
        # _tid, _pid = win32process.GetWindowThreadProcessId(hwnd)
        # if _pid in pids:
        #     return hwnd
        # GetWindow(hwnd)
        # _pids = self.get_relative_pids(_pid)
        # if [v for v in _pids if v in pids]:
        #     return hwnd

        # if _pid in pids:
        #     return hwnd

        # title = win32gui.GetWindowText(hwnd)
        # if 'TimeKit' in title:
        #     print(title)
        # try:
        #     hwnd = win32gui.GetParent(hwnd)
        # except Exception:
        #     break
        # print(win32process.GetWindowThreadProcessId(hwnd))
        # for _ in range(50):
        #     # title = win32gui.GetWindowText(hwnd)
        #     try:
        #         hwnd = win32gui.GetParent(hwnd)
        #     except Exception:
        #         break
        # #     _tid, _pid = win32process.GetWindowThreadProcessId(hwnd)
        #     if _pid in pids:
        #         return hwnd
        #     # if 'TimeKit' in title:
        #     #     proc = psutil.Process(_pid)
        #     #     print(title, _tid, _pid, pid, [v.pid for v in proc.parents()[0].children()])
        #     if _pid == pid:
        #         return hwnd
        #     try:
        #         hwnd = win32gui.GetParent(hwnd)
        #     except Exception:
        #         break

    def set_position(self, pid, title, x, y, width, height, repaint=True):
        # hwnd = pid
        # hwnd = win32gui.GetParent(hwnd)
        hwnds = self.get_hwnd(pid, title)
        print(pid, hwnds, [x, y, width, height])
        if not hwnds:
            return
        hwnd = sorted(hwnds)[0]
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
        after = preset.get('after')
        title = preset.get('title')
        if not cmd:
            return

        while time.time() - self.tic < after:
            time.sleep(0.1)

        # if isinstance(cmd, list):
        #     cmd = shlex.join(cmd)
        # if isinstance(cmd, str):
        #     cmd = shlex.split(cmd)
        # cmd = list(shlex.shlex(cmd, posix=False, punctuation_chars=False))

        cwd = preset.get('cwd') or str(Path(cmd[0]).parent)
        _cmd = [v for v in cmd]
        for i in range(len(_cmd)):
            if not re.match(r'^[a-zA-Z]:\\.*', _cmd[i]):
                continue
            if Path(_cmd[i]).exists():
                _cmd[i] = str(Path(_cmd[i]))
                if ' ' in _cmd[i]:
                    _cmd[i] = f'"{_cmd[i]}"'

        # cmdline = ' '.join(_cmd)
        pid = self.get_pid(cmd, cwd=cwd)

        # identifier = ''.join([random.choice(
        #     string.ascii_letters + string.digits) for _ in range(16)])
        # identifier = f'{int(time.time() * 1000)}-{identifier}'

        if pid:
            print(f'[popen exist] {pid} {" ".join(_cmd)}')
        else:
            subprocess.Popen(
                ' '.join(_cmd), cwd=cwd, shell=True,
                close_fds=True,
                start_new_session=True,
                # env=dict(**os.environ, PYWINSTARTUP_IDENTIFIER=identifier)
            )
            if pos:
                time.sleep(1)
            # print(dir(proc.pid))
            # pid = self.get_identifier_pid(identifier)
            pid = self.get_pid(cmd, cwd=cwd)
            print(f'[popen start] {pid} {" ".join(_cmd)}')
            # print('[popen start]', pid, shlex.join(cmd))

        # pos = [0, 0, 100, 100]
        if pid and pos:
            self.set_position(pid, title, *pos)
