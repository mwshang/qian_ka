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