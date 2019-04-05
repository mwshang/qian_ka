import wx
from main.gui.gui import UIBase
import time
from main.common.config import PER_FRAME_TIME,observer
from main.gui.gui import RuningTaskWindow
from main.common.constants import *
import threading
from main.utils.utils import fmtTime


class TileListUI(UIBase):
    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, title=u"任务列表面板", pos=wx.DefaultPosition, size=wx.Size(300, 240),
                         style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT))

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_panel7 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel7.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVEBORDER))

        bSizer27 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_btnRefreshNow = wx.Button(self.m_panel7, wx.ID_ANY, u"立即刷新", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer27.Add(self.m_btnRefreshNow, 0, wx.ALL, 5)

        self.m_btnLoadCookie = wx.Button(self.m_panel7, wx.ID_ANY, u"Load Cookie", wx.DefaultPosition, wx.DefaultSize,
                                         0)
        bSizer27.Add(self.m_btnLoadCookie, 0, wx.ALL, 5)

        self.m_panel7.SetSizer(bSizer27)
        self.m_panel7.Layout()
        bSizer27.Fit(self.m_panel7)
        bSizer6.Add(self.m_panel7, 1, wx.EXPAND | wx.ALL, 5)

        bSizer5.Add(bSizer6, 0, 0, 5)

        bSizer18 = wx.BoxSizer(wx.VERTICAL)

        self.m_panelRT = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panelRT.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVEBORDER))

        bSizer23 = wx.BoxSizer(wx.VERTICAL)

        self.m_stName2 = wx.StaticText(self.m_panelRT, wx.ID_ANY, u"任务名称:新浪财经", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_stName2.Wrap(-1)
        bSizer23.Add(self.m_stName2, 0, wx.ALL, 5)

        self.m_stEndTime = wx.StaticText(self.m_panelRT, wx.ID_ANY, u"结束时间:", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_stEndTime.Wrap(-1)
        bSizer23.Add(self.m_stEndTime, 0, wx.ALL, 5)

        bSizer26 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_btnTaskFinished = wx.Button(self.m_panelRT, wx.ID_ANY, u"任务完成", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer26.Add(self.m_btnTaskFinished, 0, wx.ALL, 5)

        self.m_btnGetReward = wx.Button(self.m_panelRT, wx.ID_ANY, u"领取奖励", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer26.Add(self.m_btnGetReward, 0, wx.ALL, 5)

        bSizer23.Add(bSizer26, 10, wx.EXPAND, 5)

        self.m_panelRT.SetSizer(bSizer23)
        self.m_panelRT.Layout()
        bSizer18.Add(self.m_panelRT, 0, wx.ALL | wx.EXPAND, 5)

        bSizer5.Add(bSizer18, 0, 0, 5)

        self.SetSizer(bSizer5)
        self.Layout()
        self.m_statusBar = self.CreateStatusBar()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_btnRefreshNow.Bind(wx.EVT_BUTTON, self.OnRefreshNow)
        self.m_btnLoadCookie.Bind(wx.EVT_BUTTON, self.OnLoadCookie)
        self.m_btnTaskFinished.Bind(wx.EVT_BUTTON, self.OnTaskFinished)
        self.m_btnGetReward.Bind(wx.EVT_BUTTON, self.OnGetReward)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnRefreshNow(self, event):
        event.Skip()

    def OnLoadCookie(self, event):
        event.Skip()

    def OnTaskFinished(self, event):
        event.Skip()

    def OnGetReward(self, event):
        event.Skip()


class TileListWindow(TileListUI):
    def __init__(self,taskList):
        super().__init__(None)
        # self.SetSize(wx.Size(400,200))

        self.taskList = taskList
        self.SetTitle(f'{self.taskList.cfg.get("name")}')

        self.session = self.taskList.session
        self.refreshAction = self.taskList.am.findGlobalActionByName("RefreshTaskList")

        self.rtLogic = RunningTaskLogic(self)

        # 普通定时器，循环调用该函数Notify，会一直进行循环
        self.timer = wx.PyTimer(self.onTick)  # 创建定时器
        self.timer.Start(PER_FRAME_TIME * 1000)  # 设置间隔时间

        self.lastTime = time.time()
        self._initUI()
        self._addObsevers()

    def _initUI(self):
        self.m_statusBar.SetFieldsCount(2)  # 状态栏分成3个区域
        self.m_statusBar.SetStatusWidths([-1, -1])  # 区域宽度比列，用负数
        self.m_statusBar.SetStatusText(self.refreshAction.refreshInfo, 0)  # 给状态栏设文字

        # self.m_panelRT.Hide()



    def _addObsevers(self):
        self.addObserver({'type':MSG_UPDATE_TILELIST_STATUS,'callback':self._updateErrorStatusText})


    def _updateErrorStatusText(self,param):
        self.SetErrorStatusText(param.get("msg"))

    def SetErrorStatusText(self, text):
        self.SetStatusText(text,1)  # 给状态栏设文字

    def onTick(self):
        delta = time.time() - self.lastTime
        self.rtLogic.tick(delta)
        self.lastTime = time.time()

        if self.rtLogic.hasRunning():
            self.SetStatusText("正在做任务中......")
        else:
            self.SetStatusText(self.refreshAction.refreshInfo, 0)  # 给状态栏设文字

    def OnRefreshNow(self,event):
        print("OnRefreshNow------start called.....")
        self.taskList.resetRefresh()



    def OnLoadCookie(self,event):
        self.reloadCookie()
        self.SetErrorStatusText('')
        print("OnLoadCookie------called finished!!!!")


    def OnTaskFinished( self, event ):
        self.rtLogic.OnTaskFinished()

    def OnGetReward(self, event):
        self.rtLogic.OnGetReward()

    def Destroy(self):
        super().Destroy()

class RunningTaskLogic():
    def __init__(self,taskListView):
        self.taskListView = taskListView
        self.taskList = self.taskListView.taskList

        self.taskListView.addObserver({'type': MSG_ACCEPTED_ATASK, 'callback': self.OnAcctedTask})
        # self.taskListView.addObserver({'type': MSG_TASK_FINISHED, 'callback': self._onTaskFinished})

        self.m_panelRT = self.taskListView.m_panelRT
        self.m_panelRT.Hide()

        self.m_stName2 = self.taskListView.m_stName2
        self.m_stEndTime = self.taskListView.m_stEndTime

        self.rtData = None

    def hasRunning(self):
        return self.rtData != None

    def OnAcctedTask(self,param):
        self.rtData = param
        self.m_panelRT.Show()

        self.m_stName2.SetLabelText(self.rtData.name)

    def OnTaskFinished( self):
        self.taskList.clearRunningTask()
        self.taskList.resetRefresh()
        self.m_panelRT.Hide()

        global observer
        observer.send(MSG_TASK_FINISHED)

        self.rtData = None

    def OnGetReward(self):
        res = self.taskList.cfg.getReward()
        # TODO

    def tick(self,delta):
        if self.rtData:
            t = self.rtData.expire_at - time.time()
            self.m_stEndTime.SetLabelText(f"结束时间:{str(fmtTime(int(t)))}")
            if t <= 0:
                self.OnTaskFinished()


