#!/usr/bin/env python

# coding=utf-8

import wx


class MyTestEvent(wx.PyCommandEvent):  # 1 定义事件

    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)

        self.eventArgs = ""

    def GetEventArgs(self):
        return self.eventArgs

    def SetEventArgs(self, args):
        self.eventArgs = args


myEVT_MY_TEST = wx.NewEventType()  # 2 创建一个事件类型

EVT_MY_TEST = wx.PyEventBinder(myEVT_MY_TEST, 1)  # 3 创建一个绑定器对象


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(300, 300), pos=(300, 300))

        panel = wx.Panel(self, -1)

        self.button1 = wx.Button(panel, id=-1, pos=(40, 40), label="button1")

        self.Bind(wx.EVT_BUTTON, self.OnButton1Click, self.button1)

        self.Bind(EVT_MY_TEST, self.OnHandle)  # 4绑定事件处理函数

    def OnButton1Click(self, event):
        self.OnDoTest()

    def OnHandle(self, event):  # 8 事件处理函数

        dlg = wx.MessageDialog(self, event.GetEventArgs(), 'A Message Box', wx.OK | wx.ICON_INFORMATION)

        dlg.ShowModal()

        dlg.Destroy()

    def OnDoTest(self):
        evt = MyTestEvent(myEVT_MY_TEST, self.button1.GetId())  # 5 创建自定义事件对象

        evt.SetEventArgs("test event")  # 6添加数据到事件

        self.GetEventHandler().ProcessEvent(evt)  # 7 处理事件


if __name__ == '__main__':
    app = wx.PySimpleApp()

    frame = MyFrame()

    frame.Show(True)

    app.MainLoop()