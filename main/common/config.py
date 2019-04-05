
from pickle import dumps,loads
import time
from main.utils.utils import *
import json
from main.common.observer import Observer


QTY_REWARD_THRESHOLD = 1200

FPS = 12
PER_FRAME_TIME = 1/FPS # 每一帧的时间
PRINT_DELTA = FPS * 5

observer = Observer()

class TryplayCfg():
    def __init__(self,account):
        self.account = account
        self.cfg = self._getCfg()
        self.headers = self.cfg.get("headers")

    def get(self,prop):
        return self.cfg.get(prop)

    def createAcceptTaskAction(self,taskList,datas):
        return createInstanceByAbsClass(self.get("AcceptTaskAction"),taskList, datas)

    def request(self,session,url,headers,data=None,method='get'):#post

        try:
            if method == 'get':
                return session.get(url,headers=headers)
            else:
                return session.post(url, data=data, headers=headers)

        except:
            return ResponseData().fill(status_code=500)

    def refreshTaskList(self,session):
        url = self.cfg.get("task_list_url")
        return self.request(session, url, self.headers, method='get')


    def acceptTask(self,session,taskId):
        raise Exception("acceptTask need impl by sub class.....")

    '''
        return {
            'expire_at':'结束时间'，
            'response':返回结果
            'taskId':taskId
        }
    '''
    def getRunningTaskInfo(self,session,taskId):
        raise Exception("getRunningTaskInfo need impl by sub class.....")


# Tryplay_QianKa ,Tryplay_MapzqqCfg

# ACCOUNT  = "13439424765"
# currentTryplayCfg =  createInstanceByAbsClass("main.mapzqq.config.Tryplay_Mapzqq",ACCOUNT)
# currentTryplayCfg =  createInstanceByAbsClass("main.qianka.config.Tryplay_QianKa",ACCOUNT)
# currentTryplayCfg = Tryplay_QianKa(ACCOUNT)
