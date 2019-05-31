# encoding: utf-8


'''
author: Taehong Kim / Jaehoon Jung
email: peppy0510@hotmail.com
'''


import os
import subprocess
import sys

try:
    from .wininstance import get_current_real_cwq
except Exception:
    from wininstance import get_current_real_cwq


class KakaoTalk():

    exe_path = os.path.join('assets', 'kakaotalk', 'KakaoTalkNoAdv.v1.1.0.exe')
    patched = False

    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self.exe_path = os.path.join(sys._MEIPASS, self.exe_path)
        else:
            # cwd = os.path.dirname(os.path.dirname(get_current_real_cwq()))
            cwd = os.path.dirname(get_current_real_cwq())
            self.exe_path = os.path.join(cwd, self.exe_path)

    def run_patch(self):
        command = self.exe_path
        subprocess.call(command, shell=True)
        self.patched = True


if __name__ == '__main__':
    kakaotalk = KakaoTalk()
    kakaotalk.run_patch()
