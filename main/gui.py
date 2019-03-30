import wx
import time
import threading

try:
    from main.entry import app
except:
    app = wx.App(0)

# def _openView(View,*args):
#     view = View(*args)
#     view.openView()
#
# def OpenView(View,*args):
#
#     timer = threading.Timer(0.1, _openView, (View,*args))
#     timer.setDaemon(True)
#     timer.start()
#
#     time.sleep(5999)


class RuningTaskWindow(wx.Frame):

    def __init__(self,expire_at,owner=None, parent=None, id=-1):
        wx.Frame.__init__(self, parent, id, '正在进行时任务面板',
                          size=(500, 400))
        # 过期时间
        self.expire_at = expire_at
        self.owner = owner
        self.bgColor = "Green"

        self._initUI()

    def _initUI(self):
        self.panel = wx.Panel(self)
        self.button = wx.Button(self.panel,
                                label="点击设置任务已做完", pos=(0, 50))
        self.display = wx.TextCtrl(self.panel, -1, '', style=wx.TE_RIGHT)
        self.display.AppendText('9')

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick,
                  self.button)  # 1 绑定按钮事件
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroyWindow)

        # 创建定时器
        self.timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)  # 绑定一个定时器事件
        self.timer.Start(1000)

    def setExpireAt(self,expire_at):
        self.expire_at = expire_at

    def handleWarning(self):
        self.bgColor = 'Green' if self.bgColor == 'Red' else 'Green' if self.bgColor == 'Red' else 'Red'
        self.panel.SetBackgroundColour(self.bgColor)
        self.panel.Refresh()

    def OnTimer(self, evt):  # 显示时间事件处理函数
        t = self.expire_at - time.time()
        self.display.SetLabelText(str(int(t)))
        if t < 100:
            self.handleWarning()

    def OnButtonClick(self, event):
        self.Close(True)

    def onDestroyWindow(self, event=None):
        if hasattr(self.owner,"setFinised"):
            self.owner.setFinised(True)

    def openView(self):
        self.Show()
        app.MainLoop()

    @staticmethod
    def create(expire_at,owner):
        frame = RuningTaskWindow(expire_at,owner)
        return frame


if __name__ == '__main__':
    # RuningTaskWindow.create(time.time()+101,{"d":1}).openView()
    OpenView(RuningTaskWindow,time.time()+101,{"d":1})

