# encoding: utf-8


__version__ = '0.0.1'
__author__ = 'Taehong Kim'
__email__ = 'peppy0510@hotmail.com'
__license__ = ''
__doc__ = '''
'''


import wx
import wx.adv

from base import StartUpWatcher
from base import kill_existing_instances
from base import run_as_admin


class TaskBarIcon(wx.adv.TaskBarIcon):

    TRAY_TOOLTIP = 'STARTUP %s' % __version__
    TRAY_ICON = 'assets\\icon.ico'

    def __init__(self, parent):
        super(TaskBarIcon, self).__init__()
        self.parent = parent
        self.set_icon(self.TRAY_ICON)

    def CreatePopupMenu(self):
        self.menu = wx.Menu()
        self.menu.SetTitle('STARTUP %s' % __version__)
        self.create_menu_item('Author: %s' % __author__)
        self.create_menu_item('Email: %s' % __email__)
        self.menu.AppendSeparator()
        self.create_menu_item('Quit STARTUP', self.parent.OnClose)
        return self.menu

    def create_menu_item(self, label, func=None):
        item = wx.MenuItem(self.menu, -1, label)
        self.menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        self.menu.Append(item)
        return item

    def set_icon(self, path):
        if path.lower().endswith('.ico'):
            icon = wx.Icon(path)
        else:
            icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, self.TRAY_TOOLTIP)


class MainFrame(wx.Frame):

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, size=wx.Size(0, 0))
        self.taskbar = TaskBarIcon(self)
        self.startup_watcher = StartUpWatcher(self)

    def OnClose(self, event=None):
        self.startup_watcher.Stop()
        wx.CallAfter(self.taskbar.Destroy)
        wx.CallAfter(self.Destroy)
        print('OnClose')


class StartUpApp(wx.App):

    def __init__(self, parent=None, *argv, **kwargs):
        wx.App.__init__(self, parent, *argv, **kwargs)

    def FilterEvent(self, event):
        return -1

    def OnPreInit(self):
        self.MainFrame = MainFrame()

    def OnClose(self, event=None):
        pass

    def __del__(self):
        pass


def main():
    app = StartUpApp()
    app.MainLoop()


if __name__ == '__main__':
    kill_existing_instances()
    main()
    # run_as_admin(main, __file__)
