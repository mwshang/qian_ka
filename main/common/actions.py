import logging
import threading
import time
import json
import random
from main.gui.gui import RuningTaskWindow

logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Action(object):
    def __init__(self):
        self.name = "Action"
        self._isFinished = False

    def enter(self):
        logger.debug("enter---->" + self.name)
        self._isFinished = False

    def exit(self):
        self._isFinished = False
        logger.debug(f'{self.name} is finished!!!!!')

    def tick(self,delta):
        if not self.isFinished():
            self._doTick(delta)

    def _doTick(self,delta):
        pass

    def isFinished(self):
        return self._isFinished

    def setFinised(self,v):
        self._isFinished = v

class RefreshTaskList(Action):
    def __init__(self,taskList):
        super().__init__()
        self.taskList = taskList

        self.lastTime = 0
        self.refresh_tasklist_delta_min = self.taskList.getCfgValue("refresh_tasklist_delta_min") 
        self.refresh_tasklist_delta_max = self.taskList.getCfgValue("refresh_tasklist_delta_max") 
        self.deltaTime = self.refresh_tasklist_delta_min

    def enter(self):
        self.lastTime = 0

    def _doTick(self,delta):
        if not self.taskList.hasRunningTask():#如果当前没有运行的任务
            t = time.time() - self.lastTime
            if t >= self.deltaTime:
                self.taskList.refresh()
                self.lastTime = time.time()
                self.deltaTime = int(random.uniform(self.refresh_tasklist_delta_min,self.refresh_tasklist_delta_max))

class RunningTaskAction(Action):
    def __init__(self,taskList,task):
        super().__init__()
        self.taskList = taskList
        self.task = task
        self.name = "RunningTaskAction"


    def enter(self):
        logger.debug(f"RunningTaskAction::enter begin to get running task,id={self.task.id}")
        response = self.taskList.getRunningTaskInfo(self.task.id)
        self._handleResponse(response)


    def _handleResponse(self, response):
        if response.get("err_code") == 0:

            self.nowTime = time.time()
            # payload = response.get("payload")
            # self.expire_at = payload.get("expire_at")
            self.expire_at = response.get("expire_at")
            self.flag = True

            if self.expire_at > 0:
                # timer = threading.Timer(0.1, self._showRunningTaskWindow, (self.expire_at, response))
                # timer.setDaemon(True)
                # timer.start()
                RuningTaskWindow.create(self.expire_at, self).openView()

    def _showRunningTaskWindow(self,expire_at,response):
        RuningTaskWindow.create(expire_at, self).openView()

    def _doTick(self,delta):
        if self.flag:
            dt = self.expire_at - self.nowTime
            if dt <= 0:
                self.setFinised(True)
            logger.debug(f"RunningTaskAction::tick running task id={self.task.id}, dt={dt}")

    def setFinised(self,v):
        super().setFinised(v)
        self.task.setRuningStatus()



class BatchExecuteAction(Action):
    def __init__(self,taskList,datas,batch=1,executCB=None):
        super().__init__()
        self.name = "BatchExecuteAction"
        self.taskList = taskList
        self.datas = datas
        self.batch = batch
        self.executCB = executCB
        self.itemRetry = self.taskList.getCfgValue("accept_retry_count") # 单个任务失败重试次数
        self.accept_task_min_delay = self.taskList.getCfgValue("accept_task_min_delay")
        self.accept_task_max_delay = self.taskList.getCfgValue("accept_task_max_delay")

        self.startIndex = 0
        self.size = 0

    def enter(self):
        super().enter()
        if self.datas == None or len(self.datas) == 0:
            self.setFinised(True)
            return

        for data in self.datas:
            self._executeData(data)


    def _isBreakFor(self):
        return self.taskList.hasRunningTask()

    def _executeData(self,data):
        retry = self.itemRetry
        while retry > 0:
            if self._isBreakFor():
                break
            logger.debug(f"_executeData retry={retry} id={data.id} qty={data.qty}")
            if self._executeData_1(data):
                break
            delay = random.uniform(self.accept_task_min_delay,self.accept_task_max_delay)
            time.sleep(delay)
            retry -= 1

    def _executeData_1(self, data):
        return False



