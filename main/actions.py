import logging
import threading
from main.config import *
import time
import json

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

class DoTaskAction(Action):
    def __init__(self,taskDetail):
        self.taskDetail = taskDetail

class BatchExecuteAction(Action):
    def __init__(self,datas,batch=3,executCB=None):
        super().__init__()
        self.name = "BatchExecuteAction"
        self.datas = datas
        self.batch = batch
        self.executCB = executCB
        self.startIndex = 0
        self.size = 0

    def enter(self):
        super().enter()
        if self.datas == None or len(self.datas) == 0:
            self.setFinised(True)
            return
        self.startIndex = 0
        self.size = len(self.datas)

    def _doTick(self,delta):
        if self.startIndex >= self.size:
            self.setFinised(True)
            return
        stIndex = self.startIndex
        endIndex = min(stIndex + self.batch - 1,self.size)
        for k in range(stIndex,endIndex):
            data = self.datas[k]
            self._executeData(data)
            if self.executCB != None:
                self.executCB(data)

        self.startIndex = endIndex + 1

    def _executeData(self,data):
        pass

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
        self._handleResponse(response)

    def _handleResponse(self,response):
        pass

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

    def tick(self,delta):
        if self.flag:
            dt = self.expire_at - self.nowTime
            if dt <= 0:
                self.setFinised(True)
            logger.debug(f"QianKaRunningTaskAction::tick running task id={self.task.id}, dt={dt}")

class QianKaBatchAcceptTaskAction(BatchExecuteAction):
    def __init__(self,taskList,datas,batch=4,threadBatch=2):
        super().__init__(datas,batch)
        self.threadBatch = threadBatch
        self.taskList = taskList
        self.name = "QianKaBatchAcceptTaskAction"
        # 接受任务请求
        self.task_start = QIANKA_SUBTASK_START

    def _executeData(self, task):
        for i in range(1, self.threadBatch):
            t = threading.Thread(target=self.acceptTask, args=(task,))
            t.start()

    def acceptTask(self,data):
        # logger.info("acceptTask--->" + str(task.get("id")) + "  " + threading.current_thread().getName())
        # if True:
        #     return
        task = data.get("task")
        taskId = task.id
        url = self.task_start.format(taskId)
        response = self.taskList.session.get(url, headers=QIANKA_TASK_HEADERS)
        response = json.loads(response.content)
        err_code = response.get("err_code")
        if err_code == 0:
            payload = response.get("payload")
            type = payload.get("type")
            if type == 1:  # "排队中，请耐心等待..."
                logger.debug(f"Please wait patiently in the queue.....taskId={taskId}")
            elif type == 2:  # 成功接受任务
                task.updateStatus(2)
                self.taskList.setRunningTask(task)
                # r = self.taskList.session.get(self.subtask_detail.format(task.get("id")),headers=self.headers)
                logger.info("acceptTask:Congratulations on getting the job!!!!!!!")
            else:
                logger.debug(f"acceptTask:unhandled type={type}")
            logger.debug("acceptTask:success to get a task!")
        else:
            logger.debug("acceptTask:get a task failed!err_code=" + err_code)

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
