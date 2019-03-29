import time

import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ActionManager:
    def __init__(self):
        self.actions = []
        self.curAction = None
        self.id = "ActionManager_id" + str(time.time())
        self.lastTickTime = time.time()

    def destroy(self):
        pass

    def start(self):
        self.lastTickTime = time.time()

    def addAction(self,action):
        self.actions.append(action)

    def _delAction(self,action):
        action.exit()

    def tick(self,delta):
        # logger.debug("begin tick..........")
        if self.curAction:
            if self.curAction.isFinished() == True:
                self.curAction.exit()
                self.curAction = None

        if self.curAction == None:
            if len(self.actions) > 0:
                self.curAction = self.actions.pop(0)
                self.curAction.enter()

        if self.curAction and self.curAction.isFinished() == False:
            delta = time.time() - self.lastTickTime
            self.curAction.tick(delta)
            self.lastTickTime = time.time()

            # logger.debug("end tick..........")

    def clear(self):
        if self.curAction:
            self.curAction.exit()
            self.curAction = None
            if len(self.actions) > 0:
                for a in self.actions:
                    a.exit()
                self.actions = []
