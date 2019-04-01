import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskVO():
    def __init__(self):
        self.id = 0  # 每次的ID可能不一样
        self.is_quality = 0 # 如果为付费应用,这儿显示的1,不是显示的0
        self.qty = 0  # 数量
        self.reward = 0  # 奖励 比如1.5
        self.type = 1  # 1标准任务,4预告任务(incomming)
        self.zs_reward = "0.00"
        self.status = 1 # //2表示正在进行任务
        self.icon = None # 图标
        self.is_pay = 0 #当为付费应用时,这里显示的1,不是显示的为0
        self.bid = None
        self.appstore_cost = 0 # //应用需要下载的价格
        self.title = None # "百***"
        self.status_for_order = 1 #当status=2(正在进行的任务)时,这里为1,当status=1时,这儿显示的是2
        self.end_at = 0

        self.tags = None

    def fill(self,task):
         for k in task:
            # self[k] = task[k]
            if hasattr(self,k):
                setattr(self,k,task[k])
            else:
                logger.debug("fill discard a attr,key=" + str(k))

    def isRunning(self):
        return self.status == 2

    def updateStatus(self,v):
        self.status = v

    def setRuningStatus(self):
        self.status = 2

class IncomingTaskVO(TaskVO):
    def __init__(self):
        super().__init__()
        self.start_date = None
        self.reservation_qty = 0
        self._sdKey = -1

    def fill(self,task):
        super().fill(task)
        self._initStartDate()

    def _initStartDate(self):
        if self._sdKey == -1:
            if self.start_date:
                arr = self.start_date.split(" ")
                # if arr[0] == '\u4eca\u65e5':
                #     logger.debug("今日")

                self._sdKey = arr[len(arr)-1]
                # self._sdKey = self._sdKey.replace(":","_")

    def getStartDateKey(self):
        return self._sdKey


class Mapzqq_TaskVO(TaskVO):
    def __init__(self):
        super().__init__()
        self.user_id = 0 # customer_id
        self._isRunningTask = False

    def fill(self,task):

        self.id = task.get("id")
        self.qty = task.get("total")
        self.reward = task.get("singleMoney")
        self.title = task.get("name")
        self.end_at = task.get("end_at") # 2019-03-31 21:21:01 这儿格式还需要统一一下

        self.user_id = task.get("user_id")
        self.useTotal = task.get("useTotal")
        self.keyword = task.get("keyword")
        self.logo = task.get("logo")
        self.effectDesc = task.get("effectDesc") #"iPad专属

    def fillRuningTask(self,task):
        self.id = task.get("task_id")
        self.user_id = task.get("customer_id")
        self.keyword = task.get("keyword")
        self.logo = task.get("logo")
        self.effectDesc = task.get("effectDesc")  # "iPad专属
        self._isRunningTask = True

    def isRunning(self):
        return self._isRunningTask