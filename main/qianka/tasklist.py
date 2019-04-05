import time
import functools
import threading

from main.common.tasklist import TaskList
from main.common.vo import TaskVO,IncomingTaskVO
from main.qianka.actions import QianKaBatchAcceptTaskAction
from main.common.constants import *
from main.common.config import observer

# 钱咖任务列表
class QianKaTaskList(TaskList):
    def __init__(self,cfg):
        super().__init__(cfg)
        self._incTasks = None

    def tick(self,delta):
        super().tick(delta)

    # 获取返回中的标准任务
    def _getStdTasksByResponse(self, response):
        return response['payload']['tasks']

    # 获取返回中的预告任务
    def _getIncomingTasksByResponse(self, response):
        return response['payload']['incoming']

    def _initStdTasks(self,tasks,response):
        if tasks != None:

            self.stdTasks = []  # 标准任务

            runningTask = None  # 正在进行的任务

            for task in tasks:
                if task.get("qty") > 0 or task.get('status') == 2:
                    vo = TaskVO()
                    vo.fill(task)
                    if vo.isRunning():
                        runningTask = vo
                    else:
                        self.stdTasks.append(vo)

            self.stdTasks = sorted(self.stdTasks,key=lambda task:task.qty,reverse=True)

            if runningTask:
                self.setRunningTask(runningTask)
            else:
                arr = self.getQtyGT0Tasks()
                if len(arr) > 0:
                    action = self.cfg.createAcceptTaskAction(self,arr)
                    self.am.addAction(action)
                else:
                    print("暂时没有任务可接受!!!")

    def getQtyGT0Tasks(self):#获取数量大于0的任务
        rst = []
        for task in self.stdTasks:
            if task.qty > 0:
                rst.append(task)

        return rst

    # 初始化预告任务
    def _initIncomingTasks(self, tasks):
        if tasks != None:
            self.incomingStartDates = {}
            self.incomingTasks = []
            for task in tasks:
                vo = IncomingTaskVO()
                vo.fill(task)
                self.incomingTasks.append(vo)
                sdKey = vo.getStartDateKey()
                if self.incomingStartDates.get(sdKey) == None:
                    self.incomingStartDates[sdKey] = []
                self.incomingStartDates[sdKey].append(vo)

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
                    # timer.setDaemon(True)
                    # timer.start()
                    # self.incomingListeners.append({'timer': timer, "key": k})
                    self.msgQueue.put({'name':MSG_INCOMMING_HANDLE,'args':(tasks,dt)})
                    # global observer
                    # observer.send(MSG_ADD_INCOMMING_LISTENER,(tasks,dt))
                    break

    def _timerCB(self,tasks,key):
        # 到达指定时间后,请求指定的任务
        print("start calling....")

        tasks.sort(key=functools.cmp_to_key(self.sorCallback))
        action = self.cfg.createAcceptTaskAction(self, tasks)
        self.am.addAction(action)


    '''
    def onIncommingTimeout(self,evt):
        super().onIncommingTimeout(evt)
        self._incTasks.sort(key=functools.cmp_to_key(self.sorCallback))
        action = self.cfg.createAcceptTaskAction(self, self._incTasks)
        self.am.addAction(action)
     '''
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

