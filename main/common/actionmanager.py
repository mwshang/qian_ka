import time

import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ActionManager:
    def __init__(self):
        self.actions = []
        self.curAction = None
        self.globalActions = []
        self.globalActionsSize = 0
        self.id = "ActionManager_id" + str(time.time())
        self.lastTickTime = time.time()

    def destroy(self):
        pass

    def start(self):
        self.lastTickTime = time.time()

    def findActionByClass(self,Class):
        if self.curAction != None:
            if isinstance(self.curAction,Class):
                return self.curAction
        for action in self.actions:
            if isinstance(action,Class):
                return action
        for action in self.globalActions:
            if isinstance(action,Class):
                return action
        return None

    def findGlobalActionByName(self,name):
        for action in self.globalActions:
            if action.name == name:
                return action

        return None

    def addAction(self,action):
        self.actions.append(action)

    def addGlobalAction(self,action):
        self.globalActions.append(action)
        self.globalActionsSize += 1

        action.enter()    

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

        if self.globalActionsSize > 0:
            for i in range(self.globalActionsSize-1,-1,-1):
                action = self.globalActions[i]
                if action.isFinished():
                    action.exit()
                    a = self.globalActions.pop(i)
                    self.globalActionsSize -= 1
                    continue
                action.tick(delta)

    def clear(self):
        if self.curAction:
            self.curAction.exit()
            self.curAction = None
            if len(self.actions) > 0:
                for a in self.actions:
                    a.exit()
                self.actions = []
