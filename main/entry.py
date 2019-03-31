from main.tasklist import *
from main.config import *
import time
import json
import wx


app = wx.App(0)


class Entry(object):

    def __init__(self):
        self._initQianKa()

    def _initQianKa(self):
        # file = open('tasklist_data.json', 'r', encoding='utf-8')
        # datas = json.load(file)
        self.taskList = QianKaTaskList(cookie_path=f"cookies/{TRYPLAY}_{ACCOUNT}.txt")
        # self.taskList.refresh()
        # self.taskList._handleRefreshResponse(datas)

    def run(self):
        lt = time.time()
        while True:
            self.taskList.tick(time.time() - lt)
            lt = time.time()
            time.sleep(PER_FRAME_TIME)


if __name__ == '__main__':
    entry = Entry()
    entry.run()