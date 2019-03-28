# 任务列表请求处理
import requests
import http.cookiejar as cookielib
import json
import logging
import time
import threading
import functools
from main.config import *
from main.vo import *
from main.actions import *
from main.actionmanager import ActionManager


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def threadCB(self,task):
    # logger.info(threading.current_thread().getName() + "   -----   ")
    self.acceptTask(task)

# 当数据大于QTY_REWARD_THRESHOLD值时,按奖励倒序排列,否则按数量倒序排序
def sorCallback(t1,t2):
    a = t1.get("task")
    b = t2.get("task")
    qty1 = a.qty
    qty2 = b.qty

    # if qty1 > QTY_REWARD_THRESHOLD and qty2 > QTY_REWARD_THRESHOLD:
    #     reward1 = a.reward
    #     reward2 = b.reward
    #     if reward1 > reward2:
    #         return -1
    # el
    if qty1 > qty2:
        return -1
    elif qty1 == qty2:
        reward1 = a.reward
        reward2 = b.reward
        if reward1 > reward2:
            return -1
    return 0

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

        self.incomingListeners = []
        self.am = ActionManager()
        self.am.start()

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

    def _handleRefreshResponse(self,response):
        #标准任务
        tasks = response['payload']['tasks']
        self._initStdTasks(tasks)
        #预告任务
        incomingTasks = response['payload']['incoming']
        self._initIncomingTasks(incomingTasks)
        self._setIncomingListeners()

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

            self.stdTasks = sorted(self.stdTasks,key=lambda task:task.qty,reverse=True)

    # 初始化预告任务
    def _initIncomingTasks(self,tasks):
        if tasks:
            self.incomingStartDates = {}
            self.incomingTasks = []
            for task in tasks:
                vo = IncomingTaskVO()
                vo.fill(task)
                self.incomingTasks.append(vo)
                sdKey = vo.getStartDateKey()
                if self.incomingStartDates.get(sdKey) == None:
                    self.incomingStartDates[sdKey] = []

                self.incomingStartDates[sdKey].append({'task':vo})

             if False:
                for k in self.incomingStartDates:
                    tasks = self.incomingStartDates[k]
                    tasks.sort(key=functools.cmp_to_key(sorCallback))
                for k in self.incomingStartDates:
                    tasks = self.incomingStartDates[k]
                    print("+++++++++++++++++++++++")
                    for v in tasks:
                        t = v.get("task")
                        print(t.qty,t.reward)
                print("--------------------------")

            self.incomingTasks = sorted(self.incomingTasks,key=lambda task:task.getStartDateKey())

    def _timeCB(self,tasks,key):
        # Caller
        # 到达指定时间后,请求指定的任务
        tasks.sort(key=functools.cmp_to_key(sorCallback))
        # BatchExecutAction
        action = BatchAcceptTaskAction(tasks)
        self.am.addAction(action)

    def _setIncomingListeners(self):
        self._clearIncomingListeners()
        self.incomingListeners = []
        for k in self.incomingStartDates:
            tasks = self.incomingStartDates[k]
            if len(tasks) > 0:
                curStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                nextStr = curStr.split(" ")[0] + " " + k + ":00"
                nt = time.mktime(time.strptime(nextStr, '%Y-%m-%d %H:%M:%S'))
                dt = nt - time.time()
                if dt > 0:
                    timer = threading.Timer(1, self._timeCB, (tasks,k))
                    timer.start()
                    self.incomingListeners.append({'timer':timer,"key":k})

    def _clearIncomingListeners(self):
        for k,v in self.incomingListeners:
            v['timer'].cancel()
        self.incomingListeners = []

    def run(self):
        while True:
            if self.runningTask == None:
                self.acceptATask()
            else:
                pass
            self.am.tick()
            time.sleep(PER_FRAME_TIME)

            # logger.info("run----------" + str(int(time.time())))
            # sys.stdout.flush()

    def acceptATask(self,batch=2):# 接受任务
        task = self.getHighQtyATask()
        if task:
            for i in range(1, batch):
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


def sorCallback1(a,b):
    qty1 = a.get("qty")
    qty2 = b.get("qty")

    if qty1 > 1000 and qty2 > 1000:
        reward1 = a.get("reward")
        reward2 = b.get("reward")
        if reward1 > reward2:
            return -1
    elif qty1 > qty2:
        return -1
    elif qty1 == qty2:
        reward1 = a.get("reward")
        reward2 = b.get("reward")
        if reward1 > reward2:
            return -1
    return 0
if __name__ == '__main__':
    file = open('tasklist_data.json', 'r', encoding='utf-8')
    datas = json.load(file)
    subTaskList = SubTaskList()
    subTaskList._handleRefreshResponse(datas)
    subTaskList.run()

    list = [
        {"qty": 500, "reward": '1.2'},
        {"qty": 1200, "reward": '3.2'},
        {"qty": 700, "reward": '1.2'},
        {"qty": 800, "reward": '1.2'},
        {"qty": 400, "reward": '1.2'},
        {"qty": 500, "reward": '1.2'},
        {"qty": 1000, "reward": '1.2'},
        {"qty": 500, "reward": '2.5'},
        {"qty": 500, "reward": '1.5'},
        {"qty": 500, "reward": '1.77'},
        {"qty": 1500, "reward": '1.25'},
        {"qty": 1500, "reward": '2.5'},
        {"qty": 2500, "reward": '1.5'},
    ]
    # list = sorted(list,key=functools.cmp_to_key(sorCallback1))
    # for t in list:
    #     print(t.get('qty'),t.get('reward'))