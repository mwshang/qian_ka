import wx
import time
from wx.grid import GridTableBase
from main.common.config import COLUMN_NAMES
import http.cookiejar as cookielib
from main.utils.utils import fmtTime

try:
    from main.entry import app
except:
    app = wx.App(0)

class UIBase(wx.Frame):
    def __init__(self,parent=None, id=wx.ID_ANY,title='',pos=wx.DefaultPosition, size=wx.Size(650, 450),style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL):
        super().__init__(parent,id=id,title=title,pos=pos,size=size,style=style)


    def saveCookie(self,name,value,domain,path = '/'):
        if len(name) > 0 and len(value) > 0:

            cookie = cookielib.Cookie(version=0, name=name, value=value, port=None, port_specified=False,
                                  domain=domain, domain_specified=False, domain_initial_dot=False, path=path,
                                  path_specified=True, secure=False, expires=999999999, discard=True, comment=None,
                                  comment_url=None, rest={}, rfc2109=False)
            self.setCookie(cookie)
            return cookie
        return None

    def setCookie(self, oCookie):
        if self.session:
            cookieJar = self.session.cookies
            try:
                # cookieJar.load()
                pass
            except Exception as e:
                pass

            cookieJar.set_cookie(oCookie)
            cookieJar.save(None,True,True)
        else:
            print("UIBase failed to setCookie,self.session = None!!!!")


class RunningTaskWindowUI(UIBase):

    def __init__(self, parent):
        super().__init__(parent=parent,title=u"运行任务面板", size=wx.Size(650, 450))


        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_CAPTIONTEXT))

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        bSizer14 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_stName = wx.StaticText(self, wx.ID_ANY, u"任务名称:新浪财经", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_stName.Wrap(-1)
        bSizer14.Add(self.m_stName, 0, wx.ALL, 5)

        bSizer14.Add((70,20))

        self.m_stEndTime = wx.StaticText(self, wx.ID_ANY, u"结束时间:", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_stEndTime.Wrap(-1)
        bSizer14.Add(self.m_stEndTime, 0, wx.ALL, 5)

        bSizer5.Add(bSizer14, 0, 0, 5)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_btnTaskFinished = wx.Button(self, wx.ID_ANY, u"任务完成", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_btnTaskFinished, 0, wx.ALL, 5)

        self.m_btnGetReward = wx.Button(self, wx.ID_ANY, u"领取奖励", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_btnGetReward, 0, wx.ALL, 5)

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
        self.m_btnTaskFinished.Bind(wx.EVT_LEFT_UP, self.OnTaskFinished)
        self.m_btnGetReward.Bind(wx.EVT_LEFT_UP, self.OnGetReward)
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
class RuningTaskWindow(RunningTaskWindowUI):

    '''
    param={
        'expire_at':'到期时间',
        'setFinishedCB':'设置任务完成回调函数',
        'taskList':'',
        'name':'任务名称'
    }
    '''
    def __init__(self,param):
        super().__init__( None)
        self.param = param
        # 过期时间
        self.expire_at = self.param.get("expire_at")
        self.setFinishedCB = self.param.get("setFinishedCB")
        self.taskList = self.param.get("taskList")
        self.session =self.taskList.session
        self.bgColor = "Green"
        taskName = self.param.get("name")
        taskName = '' if taskName == None else taskName
        self.m_stName.SetLabelText(f'任务名称:{taskName}')

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
        # self.display.SetLabelText(str(int(t)))
        self.m_stEndTime.SetLabelText(f"结束时间:{str(fmtTime(int(t)))}")
        if t < 100:
            # self.handleWarning()
            pass
        if t <= 0:
            self.OnTaskFinished(None)

    def OnTaskFinished(self, event):
        super().OnTaskFinished(event)
        self.Close(True)
        if self.setFinishedCB != None:
            self.setFinishedCB()

    def OnSetCookie(self,event):
        super().OnSetCookie(event)
        name = self.m_tcCookieKey.GetValue()
        value = self.m_tcCookieVal.GetValue()
        domain = self.m_tcCookieDM.GetValue()
        path = '/'

        self.saveCookie(name,value,domain,path)


    def onDestroyWindow(self, event=None):
        pass
        # if hasattr(self.owner,"setFinised"):
        #     self.owner.setFinised(True)



    def openView(self):
        self.Show()
        app.MainLoop()

    @staticmethod
    def create(param):
        frame = RuningTaskWindow(param)
        return frame



class TryPlayApp(wx.App):
    def OnInit(self):
        b = super().OnInit()
        self._initUI()
        return b

    def _initUI(self):
        # self.scene = TryPlayScene()
        # self.scene.Show()

        # MainFrame(None).Show()
        param = {
            'setFinishedCB': None,
            'expire_at': time.time() + 100
        }
        RuningTaskWindow.create(param).openView()

if __name__ == '__main__':
    app = TryPlayApp(False)
    # frame = wx.Frame(None, title="Demo with Notebook")
    # nb = wx.Notebook(frame)
    # nb.AddPage(cjlists(nb), "试玩赚钱")
    # nb.AddPage(cjview(nb), "Page Two")
    # nb.AddPage(cjsave(nb), "Page Three")
    # frame.Show()
    app.MainLoop()


