import logging
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

class BatchExecutAction(Action):
    def __init__(self,datas,batch=3,executCB=None):
        super().__init__()
        self.name = "BatchExecutAction"
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
            if self.executCB != None:
                self.executCB(data)

        self.startIndex = endIndex + 1

class BatchAcceptTaskAction(BatchExecutAction):
    def __init__(self,tasks):
        super().__init__(tasks,executCB=self.exeCB)
        self.name = "BatchAcceptTaskAction"


    def exeCB(self,data):
        task = data.get("task")


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
