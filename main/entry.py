from main.common.config import *
import time
import wx
from multiprocessing import Process
from main.mapzqq.config import Tryplay_MapzqqCfg
from main.qianka.config import Tryplay_QianKaCfg


from main.utils.utils import createInstanceByAbsClass


app = wx.App(0)


class Entry(object):
    def __init__(self,cfg):
        self.cfg = cfg
        self._initPlatforms()


    def _initPlatforms(self):
        self.taskList = createInstanceByAbsClass(self.cfg.get("TaskList"), self.cfg)

    def run(self):
        lt = time.time()
        while True:
            self.taskList.tick(time.time() - lt)
            lt = time.time()
            time.sleep(PER_FRAME_TIME)


def createEntry(data):
    entry = Entry(data)
    entry.run()

if __name__ == '__main__':
    datas = [
        {"platform": Tryplay_MapzqqCfg, "account": "13439424765"},
        {"platform": Tryplay_QianKaCfg, "account": "13439424765"}
    ]

    for v in datas:
        Cfg = v.get("platform")
        cfg = Cfg(v.get("account"))
        process = Process(target=createEntry,args=(cfg,))
        process.start()

    # 这儿不能去掉,否则进程会结束掉
    time.sleep(99999)