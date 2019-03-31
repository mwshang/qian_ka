import logging
import threading
from main.config import *
import time
import json
import random
from main.gui import RuningTaskWindow

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
        self.deltaTime = REFRESH_TASKLIST_DELTA_MIN

    def enter(self):
        self.lastTime = 0

    def _doTick(self,delta):
        if not self.taskList.hasRunningTask():#如果当前没有运行的任务
            t = time.time() - self.lastTime
            if t >= self.deltaTime:
                self.taskList.refresh()
                self.lastTime = time.time()
                self.deltaTime = int(random.uniform(REFRESH_TASKLIST_DELTA_MIN,REFRESH_TASKLIST_DELTA_MAX))

class RunningTaskAction(Action):
    def __init__(self,taskList,task,url):
        super().__init__()
        self.taskList = taskList
        self.task = task
        self.url = url
        self.name = "RunningTaskAction"

        self.headers = None

    def enter(self):
        logger.debug(f"RunningTaskAction::enter begin to get {self.url}")
        response = self.taskList.session.get(self.url, headers=self.headers)
        response = json.loads(response.content)
        self._handleResponse(response)

    def _handleResponse(self,response):
        pass

    def setFinised(self,v):
        super().setFinised(v)
        self.task.setRuningStatus()

class QianKaRunningTaskAction(RunningTaskAction):
    def __init__(self,taskList,task):
        url = QIANKA_SUBTASK_DETAIL.format(task.id)
        super().__init__(taskList,task,url)
        self.headers = QIANKA_TASK_HEADERS
        self.nowTime = time.time()
        self.expire_at = 0

        self.flag = False

    def _handleResponse(self, response):
        if response.get("err_code") == 0:
            payload = response.get("payload")
            self.nowTime = time.time()
            self.expire_at = payload.get("expire_at")
            self.flag = True

            RuningTaskWindow.create(self.expire_at,self).openView()

    def _doTick(self,delta):
        if self.flag:
            dt = self.expire_at - self.nowTime
            if dt <= 0:
                self.setFinised(True)
            logger.debug(f"QianKaRunningTaskAction::tick running task id={self.task.id}, dt={dt}")


class BatchExecuteAction(Action):
    def __init__(self,datas,batch=1,executCB=None,itemRetry=5):
        super().__init__()
        self.name = "BatchExecuteAction"
        self.datas = datas
        self.batch = batch
        self.executCB = executCB
        self.itemRetry = itemRetry # 单个任务失败重试次数

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
        return False

    def _executeData(self,data):
        retry = self.itemRetry
        while retry > 0:
            if self._isBreakFor():
                break
            logger.debug(f"_executeData retry={retry} id={data.id} qty={data.qty}")
            self._executeData_1(data)
            delay = random.uniform(ACCEPT_TASK_MIN_DELAY,ACCEPT_TASK_MAX_DELAY)
            time.sleep(delay)
            retry -= 1

    def _executeData_1(self, data):
        pass

class QianKaBatchAcceptTaskAction(BatchExecuteAction):
    def __init__(self,taskList,datas,batch=1,threadBatch=1,itemRetry=QIANKA_ACCEPT_RETRY_COUNT):
        super().__init__(datas,batch,itemRetry=itemRetry)
        self.threadBatch = threadBatch
        self.taskList = taskList
        self.name = "QianKaBatchAcceptTaskAction"
        # 接受任务请求
        self.task_start = QIANKA_SUBTASK_START

    def _isBreakFor(self):
        return self.taskList.hasRunningTask()

    def _executeData_1(self, task):
        for i in range(0, self.threadBatch):
            t = threading.Thread(target=self._acceptTask, args=(task,))
            t.setDaemon(True)
            t.start()

    def _acceptTask(self,task):
        logger.debug(f"准备接受任务:id={task.id} qty={task.qty}")
        taskId = task.id
        url = self.task_start.format(taskId)
        response = self.taskList.session.get(url, headers=QIANKA_TASK_HEADERS)
        response = json.loads(response.content)
        err_code = response.get("err_code")
        if err_code == 0:
            payload = response.get("payload")
            type = payload.get("type")
            if type == 1:  # "排队中，请耐心等待..."
                logger.debug(f"排队中，请耐心等待.......id={taskId} qty={task.qty}")
            elif type == 2:  # 成功接受任务
                task.updateStatus(2)
                self.taskList.setRunningTask(task)
                logger.debug(f"成功接受任务:id={task.id} qty={task.qty}")
            elif type == 3:#被封号了
                logger.debug(f"恭喜你中奖被封号了!!!!!!!!")
            else:
                logger.debug(f"_acceptTask:unhandled type={type}")
            # logger.debug("_acceptTask:success to get a task!")
        else:
            logger.debug("_acceptTask:get a task failed!err_code=" + err_code)

class CountAction(Action):
    def __init__(self,count,executeCB=None,args=None):
        super().__init__()
        self.count = count
        self.executeCB = executeCB
        self.args = args

    def _doTick(self,delta):
        super()._doTick(delta)
        if self.count <= 0:
            self.setFinised(True)
            return

        self.count -= 1
        if self.executeCB != None:
            self.executeCB(self.args)
