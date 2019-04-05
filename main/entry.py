from main.common.config import *
import time
import wx
import threading
from multiprocessing import Process
from main.mapzqq.config import Tryplay_MapzqqCfg
from main.qianka.config import Tryplay_QianKaCfg
from main.gui.tasklistui import TileListWindow
import queue


from main.utils.utils import createInstanceByAbsClass





class Entry(object):
    def __init__(self,cfg):
        self.cfg = cfg
        self.msgQueue = queue.Queue()
        self._initPlatforms()


    def _initPlatforms(self):
        self.taskList = createInstanceByAbsClass(self.cfg.get("TaskList"), self.cfg)
        self.taskList.msgQueue = self.msgQueue

        self.taskListView = TileListWindow(self.taskList,self.msgQueue)
        self.taskListView.Show()

        logic_thread = threading.Thread(target=self.taskListThread)
        logic_thread.setDaemon(True)
        logic_thread.start()


    def taskListThread(self):
        '''线程函数'''
        lt = time.time()
        while True:
            self.taskList.tick(time.time() - lt)
            lt = time.time()
            time.sleep(PER_FRAME_TIME)

    def run(self):
        pass


def createEntry(cfg):
    app = wx.App(0)
    entry = Entry(cfg)
    entry.run()
    app.MainLoop()

def startRun():
    datas = [
        {"platform": Tryplay_MapzqqCfg, "account": "13439424765"},
        {"platform": Tryplay_QianKaCfg, "account": "13439424765"}
    ]

    for v in datas:
        Cfg = v.get("platform")
        cfg = Cfg(v.get("account"))
        process = Process(target=createEntry, args=(cfg,))
        process.start()

if __name__ == '__main__':

    if False:
        startRun()
    else:
        # createEntry(Tryplay_MapzqqCfg("13439424765"))
        createEntry(Tryplay_QianKaCfg("13439424765"))


    #

    print("哎呀哎呀.............MainLoop")
    # 这儿不能去掉,否则进程会结束掉
    # time.sleep(99999)