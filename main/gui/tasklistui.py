import wx
from main.gui.gui import UIBase
import time
from main.common.config import PER_FRAME_TIME

class TileListUI(UIBase):

    def __init__(self, parent=None):
        super().__init__( parent=parent, id=wx.ID_ANY, title=u"任务列表面板", pos=wx.DefaultPosition, size=wx.Size(650, 450),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_CAPTIONTEXT))

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        bSizer14 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_stName = wx.StaticText(self, wx.ID_ANY, u"任务名称:新浪财经", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_stName.Wrap(-1)
        bSizer14.Add(self.m_stName, 0, wx.ALL, 5)

        bSizer14.Add((70, 20))

        self.m_stEndTime = wx.StaticText(self, wx.ID_ANY, u"结束倒计时:", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_stEndTime.Wrap(-1)
        bSizer14.Add(self.m_stEndTime, 0, wx.ALL, 5)

        bSizer5.Add(bSizer14, 0, 0, 5)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_btnRefreshNow = wx.Button(self, wx.ID_ANY, u"立即刷新", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_btnRefreshNow, 0, wx.ALL, 5)

        self.m_btnOpenRunningWin = wx.Button(self, wx.ID_ANY, u"打开运行任务面板", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_btnOpenRunningWin, 0, wx.ALL, 5)

        bSizer5.Add(bSizer6, 0, 0, 5)

        bSizer7 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_stCookieKey = wx.StaticText(self, wx.ID_ANY, u"name:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_stCookieKey.Wrap(-1)
        bSizer7.Add(self.m_stCookieKey, 0, wx.ALL, 5)

        self.m_tcCookieKey = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer7.Add(self.m_tcCookieKey, 0, wx.ALL, 5)

        self.m_stCookieVal = wx.StaticText(self, wx.ID_ANY, u"Value:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_stCookieVal.Wrap(-1)
        bSizer7.Add(self.m_stCookieVal, 0, wx.ALL, 5)

        self.m_tcCookieVal = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer7.Add(self.m_tcCookieVal, 0, wx.ALL, 5)

        self.m_stCookieDM = wx.StaticText(self, wx.ID_ANY, u"domain:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_stCookieDM.Wrap(-1)
        bSizer7.Add(self.m_stCookieDM, 0, wx.ALL, 5)

        self.m_tcCookieDM = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer7.Add(self.m_tcCookieDM, 0, wx.ALL, 5)

        self.m_btnSetCookie = wx.Button(self, wx.ID_ANY, u"设置cookie", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer7.Add(self.m_btnSetCookie, 0, wx.ALL, 5)

        bSizer5.Add(bSizer7, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer5)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_btnRefreshNow.Bind(wx.EVT_LEFT_UP, self.OnTaskFinished)
        self.m_btnOpenRunningWin.Bind(wx.EVT_LEFT_UP, self.OnGetReward)
        self.m_btnSetCookie.Bind(wx.EVT_LEFT_UP, self.OnSetCookie)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnTaskFinished(self, event):
        event.Skip()

    def OnGetReward(self, event):
        event.Skip()

    def OnSetCookie(self, event):
        event.Skip()


class TileListWindow(TileListUI):
    def __init__(self,taskList):
        super().__init__()

        self.taskList = taskList

        # 普通定时器，循环调用该函数Notify，会一直进行循环
        self.timer = wx.PyTimer(self.onTick)  # 创建定时器
        self.timer.Start(PER_FRAME_TIME * 1000)  # 设置间隔时间

        self.lastTime = time.time()

    def onTick(self):
        delta = time.time() - self.lastTime
        self.taskList.tick(delta)

