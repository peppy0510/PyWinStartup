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

from .wininstance import get_current_real_cwq


class NateOn():

    source_root = os.path.join('assets', 'nateon', 'NATEON', 'Skins', 'NateRes')
    target_root = os.path.join('C:\\Program Files (x86)', 'SK Communications', 'NATEON', 'Skins', 'NateRes')

    names = ('main_view.xml', 'MessageView.xml')

    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self.source_root = os.path.join(sys._MEIPASS, self.source_root)
        else:
            cwd = os.path.dirname(get_current_real_cwq())
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
        for name in self.names:
            if not self.has_backup(name):
                return False
            if self.get_target(name) != self.get_source(name):
                return False
        return True

    def patch(self):
        for name in self.names:
            if not self.has_backup(name):
                shutil.copyfile(self.get_target_path(name), self.get_backup_path(name))
            if self.get_target(name) != self.get_source(name):
                shutil.copyfile(self.get_source_path(name), self.get_target_path(name))

    def run_patch(self):
        if ctypes.windll.shell32.IsUserAnAdmin():
            self.patch()
        else:
            command = 'powershell.exe Start-Process python nateon.py -Verb runAs'
            proc = subprocess.Popen(command, shell=True)
            proc.communicate()


'''
powershell.exe Start-Process python startmanager.py -Verb runAs
'''


if __name__ == '__main__':
    nateon = NateOn()
    if nateon.is_patched():
        print('NateOn already patched')
    else:
        nateon.run_patch()
