# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import os
import subprocess
import sys
import time

try:
    from .wininstance import get_current_real_cwd
except Exception:
    from wininstance import get_current_real_cwd


class KakaoTalk():

    exe_path = 'assets\\kakaotalk\\KakaoTalkNoAdv.v1.1.0.exe'
    patched = False
    patching = False

    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self.exe_path = os.path.join(sys._MEIPASS, self.exe_path)
        else:
            # cwd = os.path.dirname(os.path.dirname(get_current_real_cwd()))
            cwd = os.path.dirname(get_current_real_cwd())
            self.exe_path = os.path.join(cwd, self.exe_path)

    def run_patch(self):
        if self.patching:
            return
        self.patching = True
        command = self.exe_path
        # time.sleep(5)
        subprocess.call(command, shell=True)
        self.patched = True
        self.patching = False


if __name__ == '__main__':
    kakaotalk = KakaoTalk()
    kakaotalk.run_patch()
