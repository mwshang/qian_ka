import wx
import time
from wx.grid import GridTableBase
import http.cookiejar as cookielib
from main.utils.utils import fmtTime
from main.common.config import observer

try:
    from main.entry import app
except:
    app = wx.App(0)

class UIBase(wx.Frame):
    def __init__(self,parent=None, id=wx.ID_ANY,title='',pos=wx.DefaultPosition, size=wx.Size(650, 450),style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL):
        super().__init__(parent,id=id,title=title,pos=pos,size=size,style=style)

        self.observers = []

    '''
        添加观察者
        @param {owner,callback=(data) ,
                type="数据类型"
                }
    '''
    def addObserver(self, param):
        self.observers.append(param)

        global observer
        observer.addObserver(param)
    def sendMsg(self,type,data):
        global observer
        observer.send(type,data)

    '''
        删除观察者
        @param {callback=function(data) end,
                type="数据类型"
                }
    '''
    def removeObserver(self,param):
        global observer
        observer.removeObserver(param)

        _type = param.get("type")
        _cb = param.get("callback")

        for i in range(len(self.observers)-1,-1,-1):
            v = self.observers[i]
            if v.get('type') == _type and v.get("callback") == _cb:
                del[i]
                break

    # def Destroy(self):
    #     global observer
    #     for v in self.observers:
    #         observer.removeObserver(v)
    #     observer = None
    #     super().Destroy()

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

    def reloadCookie(self):
        cookieJar = self.session.cookies
        try:
            cookieJar.load()
        except Exception as e:
            print('reloadCookie',e.args)


class RefreshCookieUI(UIBase):

    def __init__(self, parent=None,title=u"重新加载Cookie"):
        super().__init__(parent=parent, title=title, size=wx.Size(200, 100))

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer19 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button14 = wx.Button(self, wx.ID_ANY, u"Load Cookie", wx.DefaultPosition, wx.Size(100, 40), 0)
        bSizer19.Add(self.m_button14, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.SetSizer(bSizer19)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_button14.Bind(wx.EVT_BUTTON, self.OnLoadCookie)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnLoadCookie(self, event):
        event.Skip()

class RefreshCookieView(RefreshCookieUI):

    def __init__(self,session,title=''):
        super().__init__(title=title)
        self.session = session
        if title:
            self.SetTitle(title)

    def OnLoadCookie(self, event):
        self.reloadCookie()


class RunningTaskWindowUI(UIBase):

    def __init__(self, parent):
        super().__init__(parent=parent,title=u"运行任务面板", size=wx.Size(650, 450))


        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNHIGHLIGHT ) )

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
		
        self.m_btnSetCookie = wx.Button( self, wx.ID_ANY, u"Load Cookie", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.m_btnSetCookie, 0, wx.ALL, 5 )

        bSizer5.Add(bSizer7, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer5)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_btnTaskFinished.Bind( wx.EVT_LEFT_UP, self.OnTaskFinished )
        self.m_btnGetReward.Bind( wx.EVT_LEFT_UP, self.OnGetReward )
        self.m_btnSetCookie.Bind( wx.EVT_BUTTON, self.OnLoadCookie )

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnTaskFinished(self, event):
        if event:
            event.Skip()

    def OnGetReward(self, event):
        if event:
            event.Skip()

    def OnLoadCookie( self, event ):
        if event:
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
        # 过期时间x`
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
        # 这儿Close会把整个App给停止掉,还未找原因
        self.Close(True)
        # self.Hide()

        if self.setFinishedCB != None:
            self.setFinishedCB()


    def OnLoadCookie( self, event ):
        super().OnLoadCookie(event)
        self.reloadCookie()
        print("reloadCookie finished!!!!")

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


