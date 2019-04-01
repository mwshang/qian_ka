import logging
import threading
import json
import time
from main.common.actions import BatchExecuteAction,RunningTaskAction
from main.gui.gui import RuningTaskWindow

logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 鼠宝批量接受任务
class MapzqqBatchAcceptTaskAction(BatchExecuteAction):
    def __init__(self,taskList,datas,batch=1,threadBatch=1):
        super().__init__(taskList,datas,batch)
        self.threadBatch = threadBatch
        self.name = "MapzqqBatchAcceptTaskAction"


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
        err_code = response.get("status")
        rst = False
        if err_code == 1:
            payload = response.get("payload")
            type = response.get("status")
            if type == 1:  # 成功接受任务
                task.updateStatus(2)
                self.taskList.setRunningTask(task)
                logger.debug(f"成功接受任务:id={task.id} qty={task.qty}")
                rst = True
            else:
                logger.debug(f"_acceptTask:unhandled type={type}")
            # logger.debug("_acceptTask:success to get a task!")
        else:
            logger.debug(f"_acceptTask:get a task failed!err_code={err_code} msg={response.get('msg')}")
        return rst