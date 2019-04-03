import logging
import threading
import time
import json
import random
from main.gui.gui import RuningTaskWindow
from main.utils.utils import fmtTime
from main.common.config import PRINT_DELTA

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

# 全局Action,刷新任务列表
class RefreshTaskList(Action):
    def __init__(self,taskList):
        super().__init__()
        self.name = 'RefreshTaskList'
        self.taskList = taskList

        self.lastTime = 0
        self.refresh_tasklist_delta_min = self.taskList.getCfgValue("refresh_tasklist_delta_min") 
        self.refresh_tasklist_delta_max = self.taskList.getCfgValue("refresh_tasklist_delta_max") 
        self.deltaTime = self.refresh_tasklist_delta_min

        self.tmpCnt = 0

    def enter(self):
        self.lastTime = 0

    def reset(self):
        self.lastTime = 0

    def _doTick(self,delta):
        if not self.taskList.hasRunningTask():#如果当前没有运行的任务
            t = time.time() - self.lastTime
            if t >= self.deltaTime:
                self.taskList.refresh()
                self.lastTime = time.time()
                self.deltaTime = int(random.uniform(self.refresh_tasklist_delta_min,self.refresh_tasklist_delta_max))
            else:
                self.tmpCnt += 1
                if self.tmpCnt % PRINT_DELTA == 0:
                    logger.debug(f"{fmtTime(self.deltaTime - int(t))} 开始刷新任务列表")

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
            self.expire_at = response.get("expire_at")
            self.flag = True

            if self.expire_at > 0:
                self.task.setRuningStatus()
                # timer = threading.Timer(0.1, self._showRunningTaskWindow, (self.expire_at, response))
                # timer.setDaemon(True)
                # timer.start()
                self._showRunningTaskWindow(self.expire_at, response)

    def _showRunningTaskWindow(self,expire_at,response):
        param = {
            'setFinishedCB':self.setFinishedCB,
            'expire_at':expire_at,
            'name':response.get("name"),
            'response':response,
            "taskList":self.taskList
        }
        RuningTaskWindow.create(param).openView()

    def setFinishedCB(self):
        self.setFinised(True)
        self.taskList.resetRefresh()

    def _doTick(self,delta):
        if self.flag:
            dt = self.expire_at - self.nowTime
            if dt <= 0:
                self.setFinised(True)
            # logger.debug(f"RunningTaskAction::tick running task id={self.task.id}, dt={dt}")

    def setFinised(self,v):
        super().setFinised(v)
        # self.task.setRuningStatus()



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
        self._dicFilter = dict({}) # {taskId:data,}如果存在该变量中,就不会进行接受任务

    def enter(self):
        super().enter()
        if self.datas == None or len(self.datas) == 0:
            self.setFinised(True)
            return

        for data in self.datas:
            self._executeData(data)
            # if self._filterExecute(data) == False:
            #     self._executeData(data)

    def _filterExecute(self,data):
        if self._dicFilter.get(str(data.id)) != None:
            return True
        return False


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



