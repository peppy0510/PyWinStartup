# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import ctypes
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin(callback, file, try_run_as_admin=True):
    if try_run_as_admin is False or is_admin():
        callback()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, file, None, 1)
