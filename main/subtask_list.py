# 任务列表请求处理
import requests
import http.cookiejar as cookielib
import json
import logging
import time
import threading
from main.config import *
import sys

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# logger.info("Start print log")
# logger.debug("Do something")
# logger.warning("Something maybe fail.")
# logger.info("Finish")

def threadCB(self,task):
    # logger.info(threading.current_thread().getName() + "   -----   ")
    self.acceptTask(task)


class SubTaskList(object):
    def __init__(self,session=None):
        self.session = session
        # 刷新任务列表请求
        self.task_url = "https://qianka.com/s4/lite.subtask.list"
        # 接受任务请求
        self.task_start = 'https://qianka.com/s4/lite.subtask.start?task_id={0}&quality={1}'
        # 获取进行中的任务详情
        self.subtask_detail = 'https://qianka.com/s4/lite.subtask.detail?task_id={0}'

        self.runningTask = None #正在进行的任务
        self.stdTasks = [] # 标准任务
        self.incomingTasks = [] #预告任务
        self.incomingStartDates = {}#预告开始时间 key=开始时间,值为任务ID数组

        self.lastRefreshTime = 0

        if self.session == None:
            self._initSession()
        self.headers = {
            "Host": "qianka.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 version=1.1.2 ",
            "Referer": "https://qianka.com/v4/tasks/lite",
        }

    def _initSession(self):
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(filename="qianka.txt")

    def refresh(self):
        self.session.cookies.load()
        response = self.session.get(self.task_url, headers=self.headers)

    def _onSortQty(self):
        return self.get("qty")

    def _handleRefreshResponse(self,response):
        #标准任务
        tasks = response['payload']['tasks']
        self._initStdTasks(tasks)
        #预告任务
        incomingTasks = response['payload']['incoming']
        self._initIncomingTasks(incomingTasks)

    def _initStdTasks(self,tasks):
        if tasks:
            self.runningTask = None  # 正在进行的任务
            self.stdTasks = []  # 标准任务

            for task in tasks:
                vo = TaskVO()
                vo.fill(task)
                if vo.isRunning():
                    self.runningTask = vo
                else:
                    self.stdTasks.append(vo)

            self.stdTasks = sorted(self.stdTasks,key=SubTaskList._onSortQty,reverse=True)

    def _initIncomingTasks(self,tasks):
        if tasks:
            self.incomingStartDates = {}

    def run(self):
        while True:
            if self.runningTask == None:
                self.acceptATask()
                time.sleep(RUN_DELTA)
            else:
                time.sleep(1)

            logger.info("run----------")
            # sys.stdout.flush()



    def acceptATask(self):# 接受任务
        task = self.getHighQtyATask()
        if task:
            for i in range(1, 5):
                t = threading.Thread(target=threadCB, args=(self,task))
                t.start()
        else:
            logger.debug("tryAcceptATask:cant get a task to accept!")

    def acceptTask(self,task):
        logger.info("acceptTask--->" + str(task.get("id")) + "  " + threading.current_thread().getName())
        if True:
            return
        url = self.task_start.format(task.get('id'), 0)
        response = self.session.get(url, headers=self.headers)
        if response.err_code == 0:
            payload = response.payload
            if payload.type == 1:  # "排队中，请耐心等待..."
                pass
            elif payload.type == 2:  # 成功接受任务
                task.updateStatus(2)
                self.runningTask = task
                # r = self.session.get(self.subtask_detail.format(task.get("id")),headers=self.headers)
                logger.info("acceptATask:Congratulations on getting the job!!!!!!!")
            else:
                pass
            logger.debug("tryAcceptATask:success to get a task!")
        else:
            logger.debug("tryAcceptATask:get a task failed!err_code=" + response.err_code)

    def getHighQtyATask(self):
        # 对数量大于等于1000的任务,选取奖励最高的任务
        # 对小于1000的选取数量最大的
        task = None

        for t in self.stdTasks:
            qty = t.get('qty')
            if qty >= 1000:
                if task == None:
                    task = t
                else:
                    if t.get("reward") > task.get("reward"):
                        task = t
            elif task == None and qty > 0:
                task = t
                break
            else:
                break
        return task

class TaskVO(dict):
    def __int__(self):
        self.id = 0  # 每次的ID可能不一样
        self.is_quality = 0 # 如果为付费应用,这儿显示的1,不是显示的0
        self.zs_reward = "0.00"
        self.status = 1 # //2表示正在进行任务
        self.icon = None # 图标
        self.is_pay = 0 #当为付费应用时,这里显示的1,不是显示的为0
        self.bid = None
        self.appstore_cost = 0 # //应用需要下载的价格
        self.title = None # "百***"
        self.reward = 0 # 奖励 比如1.5
        self.type = 1 # 1标准任务,4预告任务(incomming)
        self.status_for_order = 1 #当status=2(正在进行的任务)时,这里为1,当status=1时,这儿显示的是2
        self.qty = 0 # 数量

    def fill(self,task):
         for k in task:
            self[k] = task[k]

    def isRunning(self):
        return self.get('status') == 2

    def updateStatus(self,v):
        self['status'] = v


if __name__ == '__main__':
    file = open('tasklist_data.json', 'r', encoding='utf-8')
    datas = json.load(file)
    subTaskList = SubTaskList()
    subTaskList._handleRefreshResponse(datas)
    subTaskList.run()