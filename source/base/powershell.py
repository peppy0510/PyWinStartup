# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


from pathlib import Path


class PowerShell():

    patched = False
    patching = False

    def __init__(self):
        pass

    def run_patch(self):
        if self.patching:
            return
        self.patching = True
        paths = [
            Path.home().joinpath('AppData/Roaming').joinpath(
                'Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt'),
            # Path('//wsl.localhost/Ubuntu-20.04').joinpath(
            #     'root/.local/share/powershell/PSReadLine/ConsoleHost_history.txt'),
            # Path('//wsl.localhost/Ubuntu-22.04').joinpath(
            #     'root/.local/share/powershell/PSReadLine/ConsoleHost_history.txt'),
            # Path('//wsl.localhost/Ubuntu-24.04').joinpath(
            #     'root/.local/share/powershell/PSReadLine/ConsoleHost_history.txt'),
        ]
        for path in paths:
            if not path.exists():
                continue
            removes = []
            linesep = '\n' if 'wsl.localhost' in str(path) else '\r\n'
            with open(path, 'rb') as file:
                content = file.read().decode('utf-8')
            lines = content.split(linesep)
            for i in range(len(lines) - 1, -1, -1):
                if '�' in lines[i]:
                    removes += [lines.pop(i)]
            if not removes:
                continue
            content = linesep.join(lines)
            with open(path, 'wb') as file:
                file.write(content.encode('utf-8'))
        self.patched = True
        self.patching = False


if __name__ == '__main__':
    powershell = PowerShell()
    powershell.run_patch()
