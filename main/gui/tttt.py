import time
import wx
class MyFrame(wx.Frame):
    def __init__(self,parent=None):
        super(MyFrame, self).__init__(parent, -1, "数表控件", size=(450, 250))

        panel = wx.Panel(self,-1)
        sb = self.CreateStatusBar(2)
        sb.SetStatusWidths([100,220])

        self.count = 0
        #普通定时器，循环调用该函数Notify，会一直进行循环
        self.timer = wx.PyTimer(self.Notify)    #创建定时器
        self.timer.Start(1000)  #设置间隔时间

        self.inputText = wx.TextCtrl(panel,-1,"",pos = (10,10),size=(50,-1))
        self.inputText2 = wx.TextCtrl(panel,-1,"",pos = (10,10),size=(50,-1))
        btn = wx.Button(panel,-1,"带参数的定时器")
        btn2 = wx.Button(panel,-1,"停止")

        #在绑定的函数中去调用定时器进行开启和关闭
        self.Bind(wx.EVT_BUTTON,self.OnStart,btn)
        self.Bind(wx.EVT_BUTTON,self.OnStop,btn2)

        sizer = wx.FlexGridSizer(cols=4, vgap=10, hgap=10)
        sizer.Add(self.inputText)
        sizer.Add(self.inputText2)
        sizer.Add(btn)
        sizer.Add(btn2)
        panel.SetSizer(sizer)
        panel.Fit()

    def OnStart(self,event):
        self.timer2 = wx.CallLater(1000,self.OnCallTimer,1,2,3) #带参数的定时器

    def OnStop(self,event):
        self.timer2.Stop()      #停止定时器
        self.inputText2.Value = str(self.timer2.GetResult())        #返回参数的计算结果在第二个输入框

    def OnCallTimer(self,*args,**kwargs):
        self.count = self.count + 1     #每次调用都会对该数加一（每秒加一）
        self.inputText.Value = str(self.count)  #显示在第一个输入框
        tup = args
        total = 0
        for x in tup:
            total += x
        self.timer2.Restart(1000,total,total+1,total+2) #重启定时器
        return total

    def Notify(self):
        t = time.localtime(time.time())
        self.SetStatusText("定时器",0)
        self.SetStatusText(time.strftime("%Y-%m-%d %H:%M:%S"),1)

app = wx.App()

frame = MyFrame()
frame.Show()

app.MainLoop()
