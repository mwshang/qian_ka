
import requests
import http.cookiejar as cookielib
import logging
import time
import threading
import functools
import json

from main.actionmanager import ActionManager
from main.vo import *
from main.actions import *
from main.config import *

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskList(object):# 任务列表基类
    def __init__(self,task_list_url,accept_url,task_detail_url,cookie_path,headers=None):
        # 刷新任务列表请求
        self.task_list_url = task_list_url
        # 接受任务的URL
        self.accept_url = accept_url
        # 任务详情URL
        self.task_detail_url = task_detail_url
        # cookie文件名路径
        self.cookie_path = cookie_path

        self.headers = headers
        self.session = None

        # 正在进行的任务
        self.runningTask = None
        # 标准任务
        self.stdTasks = []
        # 预告任务
        self.incomingTasks = []
        # 预告开始时间 key=开始时间,值为任务ID数组
        self.incomingStartDates = {}
        # 预告任务监听器
        self.incomingListeners = []
        self.am = ActionManager()
        self.am.start()

        if self.session == None:
            self._initSession()

    def _initSession(self):
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(filename=self.cookie_path)

    def tick(self,delta):
        self.am.tick(delta)

    def refresh(self):
        self.session.cookies.load()
        response = self.session.get(self.task_list_url, headers=self.headers)
        self._handleRefreshResponse(response)

    def _handleRefreshResponse(self,response):
        response = json.loads(response.content)
        if self._responseIsSuccess(response):
            # 标准任务
            stdTasks = self._getStdTasksByResponse(response)
            self._initStdTasks(stdTasks)
            # 预告任务
            incomingTasks = self._getIncomingTasksByResponse(response)
            self._initIncomingTasks(incomingTasks)
            # 添加预告任务定时器
            self._setIncomingListeners()
        else:
            logger.warning(f"_handleRefreshResponse refresh task error--->{self.task_list_url}")

    def _responseIsSuccess(self,response):
        err_code = response.get("err_code")
        return err_code == 0

    # 获取返回中的标准任务
    def _getStdTasksByResponse(self,response):
        pass

    # 获取返回中的预告任务
    def _getIncomingTasksByResponse(self,response):
        pass

    # 初始化标准任务
    def _initStdTasks(self,tasks):
        pass

    # 初始化预告任务
    def _initIncomingTasks(self, tasks):
        pass

    # 添加预告任务定时器
    def _setIncomingListeners(self):
        self._clearIncomingListeners()

    def _clearIncomingListeners(self):
        for k,v in self.incomingListeners:
            v['timer'].cancel()
        self.incomingListeners = []

    # 添加正在运行的任务
    def setRunningTask(self,task):
        raise Exception("setRunningTask unimplemention......")

class QianKaTaskList(TaskList):
    def __init__(self,task_list_url=None,accept_url=None,task_detail_url=None,cookie_path=None):
        self.headers = QIANKA_TASK_HEADERS
        task_list_url = task_list_url if (task_list_url != None) else QIANKA_SUBTASK_LIST
        accept_url  = accept_url if (accept_url != None) else QIANKA_SUBTASK_START
        task_detail_url = task_detail_url if (task_detail_url != None) else QIANKA_SUBTASK_DETAIL
        cookie_path = cookie_path if (cookie_path != None) else "qianka.txt"
        super().__init__(task_list_url,accept_url,task_detail_url,cookie_path,headers=self.headers)

    # 获取返回中的标准任务
    def _getStdTasksByResponse(self, response):
        return response['payload']['tasks']

    # 获取返回中的预告任务
    def _getIncomingTasksByResponse(self, response):
        return response['payload']['incoming']

    # 添加正在运行的任务
    def setRunningTask(self, task):
        if task.isRunning():
            pass
            # self.am.clear()
            # action = RunningTaskAction(self,task,QIANKA_SUBTASK_DETAIL.format(task.id))
            # self.am.addAction(action)
        else:
            logger.warning(f"QianKaTaskList::setRunningTask task is not a running,id={task.id}")

    def _initStdTasks(self,tasks):
        if tasks:

            self.stdTasks = []  # 标准任务

            runningTask = None  # 正在进行的任务

            for task in tasks:
                vo = TaskVO()
                vo.fill(task)
                if vo.isRunning():
                    runningTask = vo
                else:
                    self.stdTasks.append(vo)

            self.stdTasks = sorted(self.stdTasks,key=lambda task:task.qty,reverse=True)

            if runningTask:
                self.setRunningTask(runningTask)

    # 初始化预告任务
    def _initIncomingTasks(self, tasks):
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
                self.incomingStartDates[sdKey].append({'task': vo})

            self.incomingTasks = sorted(self.incomingTasks, key=lambda task: task.getStartDateKey())

    # 添加预告任务定时器
    def _setIncomingListeners(self):
        super()._setIncomingListeners()
        for k in self.incomingStartDates:
            tasks = self.incomingStartDates[k]
            if len(tasks) > 0:
                curStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                nextStr = curStr.split(" ")[0] + " " + k + ":00"
                nt = time.mktime(time.strptime(nextStr, '%Y-%m-%d %H:%M:%S'))
                dt = nt - time.time()
                if dt > 0:
                    # timer = threading.Timer(dt, self._timerCB, (tasks, k))
                    # TODO
                    logger.warning("TODO _setIncomingListeners---")
                    timer = threading.Timer(1, self._timerCB, (tasks, k))
                    timer.start()
                    self.incomingListeners.append({'timer': timer, "key": k})

    def _timerCB(self,tasks,key):
        # Caller
        # 到达指定时间后,请求指定的任务
        tasks.sort(key=functools.cmp_to_key(self.sorCallback))
        action = QianKaBatchAcceptTaskAction(self,tasks)
        self.am.addAction(action)
        # TODO

    # 当数据大于QTY_REWARD_THRESHOLD值时,按奖励倒序排列,否则按数量倒序排序
    def sorCallback(self,t1, t2):
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