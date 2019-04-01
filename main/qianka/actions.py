
import logging
import threading
import json
import time
from main.common.actions import BatchExecuteAction,RunningTaskAction
from main.gui.gui import RuningTaskWindow


logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 钱咖批量接受任务
class QianKaBatchAcceptTaskAction(BatchExecuteAction):
    def __init__(self,taskList,datas,batch=1,threadBatch=1):
        super().__init__(taskList,datas,batch)
        self.threadBatch = threadBatch
        self.name = "QianKaBatchAcceptTaskAction"

    def _executeData_1(self, task):
        if False:
            for i in range(0, self.threadBatch):
                t = threading.Thread(target=self._acceptTask, args=(task,))
                t.setDaemon(True)
                t.start()
        else:
            return self._acceptTask(task)

    def _acceptTask(self,task):
        logger.debug(f"准备接受任务:id={task.id} qty={task.qty}")
        taskId = task.id
        response = self.taskList.acceptTask(taskId)
        response = json.loads(response.content)
        err_code = response.get("err_code")
        rst = False
        if err_code == 0:
            payload = response.get("payload")
            type = payload.get("type")
            if type == 1:  # "排队中，请耐心等待..."
                logger.debug(f"排队中，请耐心等待.......id={taskId} qty={task.qty}")
            elif type == 2:  # 成功接受任务
                task.updateStatus(2)
                self.taskList.setRunningTask(task)
                logger.debug(f"成功接受任务:id={task.id} qty={task.qty}")
                rst = True
            elif type == 3:#被封号了
                logger.debug(f"恭喜你中奖被封号了!!!!!!!!")
                rst = True
            else:
                logger.debug(f"_acceptTask:unhandled type={type}")
            # logger.debug("_acceptTask:success to get a task!")
        else:
            logger.debug("_acceptTask:get a task failed!err_code=" + err_code)
        return False


class QianKaRunningTaskAction(RunningTaskAction):
    def __init__(self,taskList,task):
        super().__init__(taskList,task)
        self.nowTime = time.time()
        self.expire_at = 0

        self.flag = False

    def _handleResponse(self, response):
        if response.get("err_code") == 0:

            self.nowTime = time.time()
            # payload = response.get("payload")
            # self.expire_at = payload.get("expire_at")
            self.expire_at = response.get("expire_at")
            self.flag = True

            if self.expire_at > 0:
                timer = threading.Timer(0.1, self._timerCB, (self.expire_at, response))
                timer.setDaemon(True)
                timer.start()

    def _showRunningTaskWindow(self,expire_at,response):
        RuningTaskWindow.create(expire_at, self).openView()

    def _doTick(self,delta):
        if self.flag:
            dt = self.expire_at - self.nowTime
            if dt <= 0:
                self.setFinised(True)
            logger.debug(f"QianKaRunningTaskAction::tick running task id={self.task.id}, dt={dt}")
