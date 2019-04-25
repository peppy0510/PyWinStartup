# encoding: utf-8


'''
author: Taehong Kim / Jaehoon Jung
email: peppy0510@hotmail.com
'''


import ctypes
import os
import shutil
import subprocess
import sys

try:
    from .winuac import is_admin
    from .winuac import run_as_admin
    from .wininstance import get_current_real_cwq
except Exception:
    from winuac import is_admin
    from winuac import run_as_admin
    from wininstance import get_current_real_cwq


class NateOn():

    source_root = os.path.join('assets', 'nateon', 'NATEON', 'Skins', 'NateRes')
    target_root = os.path.join('C:\\Program Files (x86)', 'SK Communications', 'NATEON', 'Skins', 'NateRes')
    hosts_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'

    names = ('main_view.xml', 'MessageView.xml')

    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self.source_root = os.path.join(sys._MEIPASS, self.source_root)
        else:
            cwd = os.path.dirname(os.path.dirname(get_current_real_cwq()))
            self.source_root = os.path.join(cwd, self.source_root)

    def get_source_path(self, name):
        return os.path.join(self.source_root, name)

    def get_target_path(self, name):
        return os.path.join(self.target_root, name)

    def get_backup_path(self, name):
        return '.'.join([os.path.join(self.target_root, name), 'bak'])

    def has_backup(self, name):
        return '.'.join([os.path.join(self.target_root, name), 'bak'])

    def get_source(self, name):
        with open(self.get_source_path(name), 'rb') as file:
            return file.read()

    def get_target(self, name):
        with open(self.get_target_path(name), 'rb') as file:
            return file.read()

    def is_patched(self):
        if self.get_unpatched_hosts():
            return False
        for name in self.names:
            if not self.has_backup(name):
                return False
            if self.get_target(name) != self.get_source(name):
                return False
        return True

    def patch(self):
        self.patch_hosts()
        for name in self.names:
            if not self.has_backup(name):
                shutil.copyfile(self.get_target_path(name), self.get_backup_path(name))
            if self.get_target(name) != self.get_source(name):
                shutil.copyfile(self.get_source_path(name), self.get_target_path(name))

    def patch_hosts(self):

        hosts = self.get_unpatched_hosts()
        with open(self.hosts_path, 'a') as file:
            file.write('\n')
            for host in hosts:
                file.write('127.0.0.1 {}  # NateOn-AD-Block\n'.format(host))

    def get_unpatched_hosts(self):
        hosts = [
            'cyad.nate.com', 'cyad1.nate.com', 'nateonevent.nate.com',
            'nateon.nate.com', 'nokw.nate.com', 'shop.nate.com',
            '203.226.255.7', '203.226.255.11', '211.234.239.59']
        path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
        with open(path, 'r') as file:
            content = file.read()
            for line in content.split('\n'):
                words = [v.strip('\n\r\t ') for v in line.strip('\n\r\t ').split(' ')]
                words = [v for v in words if v]
                for i in range(len(hosts) - 1, -1, -1):
                    if hosts[i] in words:
                        hosts.pop(i)
                        continue
        return hosts

    def run_patch(self):
        if ctypes.windll.shell32.IsUserAnAdmin():
            self.patch()
        else:
            if hasattr(sys, '_MEIPASS'):
                cwd = get_current_real_cwq()
                name = os.path.basename(cwd)
                path = os.path.join(cwd, '{}.exe'.format(name))
                # command = 'powershell.exe Start-Process -FilePath "{}" -Verb runAs'.format(path)
                command = '"{}" runasadmin'.format(path)
            else:
                command = 'powershell.exe Start-Process python nateon.py -Verb runAs'
            subprocess.call(command, shell=True)

            '''
            powershell.exe Start-Process -FilePath "C:\Program Files\PyWinStartup\PyWinStartup.exe" -Verb runAs
            powershell.exe Start-Process "C:\Program Files\PyWinStartup\PyWinStartup.exe" -Verb runAs
            '''


if __name__ == '__main__':
    nateon = NateOn()
    if nateon.is_patched():
        print('NateOn already patched')
    else:
        nateon.run_patch()
