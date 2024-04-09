# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import json

from base.dictionary import load_commented_json
from pathlib import Path

root = Path(__name__).resolve().parent
user_path = Path(f'{root}/settings.json')
default_path = Path(f'{root}/source/settings.json')

# with open(default_path, 'rb') as file:
#     default = json.loads(file.read().decode('utf-8'))

default = load_commented_json(default_path)

user = {}
if user_path.exists():
    # with open(user_path, 'rb') as file:
    #     user = json.loads(file.read().decode('utf-8'))
    user = load_commented_json(user_path)

UPTIME = user.get('UPTIME', default.get('UPTIME'))
INTERVAL = user.get('INTERVAL', default.get('INTERVAL'))
PATCH = user.get('PATCH', default.get('PATCH'))
PRESETS = user.get('PRESETS', default.get('PRESETS'))


# UPTIME = 60

# INTERVAL = 1

# PATCH = {
#     "NATEON": False,
#     "KAKAOTALK": False
# }

# PRESETS = [
#     {
#         'pname': 'Swit.exe',
#         'title': '',
#         'action': 'hide'
#     }, {
#         'pname': 'Swit.exe',
#         'title': '',
#         'action': 'hide'
#     }, {
#         'pname': 'KakaoTalk.exe',
#         'title': '카카오톡',
#         'action': 'hide'
#     }, {
#         'pname': 'WMOne.exe',
#         'title': 'WMOne',
#         'action': 'hide'
#     }, {
#         'pname': 'WMOne.exe',
#         'title': 'LINE WORKS',
#         'action': 'hide'
#     }, {
#         'pname': 'NateOnMain.exe',
#         'title': 'NateOn',
#         'action': 'hide'
#     }, {
#         'pname': 'NateOnMain.exe',
#         'title': '네이트온 안내',
#         'action': 'hide'
#     }, {
#         'pname': 'NateOnMain.exe',
#         'title': '보안 경고',
#         'action': 'hide'
#     }, {
#         'pname': 'uTorrent.exe',
#         'action': 'hide'
#     }, {
#         'pname': 'KvAppService.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'SkypeApp.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'SkypeBackgroundHost.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'AGMService.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'AGSService.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'BitTorrentAntivirus.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'acrotray.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'HancomStudio.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'HancomStudio_AD.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'HncUpdateService.exe',
#         'action': 'kill'
#     }, {
#         'pname': 'SkypeBridge.exe',
#         'action': 'kill'
#     }
# ]


# KILLPROC_PRESETS = [{
#     'pname': 'acrotray.exe'
# }, {
#     'pname': 'HancomStudio.exe'
# }, {
#     'pname': 'HancomStudio_AD.exe'
# }, {
#     'pname': 'HncUpdateService.exe'
# }, {
#     'pname': 'SkypeBridge.exe'
# }]
