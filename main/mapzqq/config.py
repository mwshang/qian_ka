import time
from main.common.config import TryplayCfg
from pickle import dumps,loads
import json
import math

#鼠宝
class Tryplay_MapzqqCfg(TryplayCfg):
    def __init__(self,account):
        super().__init__(account)
        self.rst_param = {
            "sign": "abc",
            "format": "json",
            "customer_id": "20190301zhuniandajiDDDDDc",
            "timestamp": "1554019942178",
            "taskId": 55305,
            "customerId": 939059,
            "os": "12.0+",
            "ip": ""
        }

    def _getCfg(self):
        cfg = {
            "TaskList": "main.mapzqq.tasklist.MapzqqTaskList",#任务列表
            "AcceptTaskAction": "main.mapzqq.actions.MapzqqBatchAcceptTaskAction", #接受任务Action
            #刷新任务列表URL
			"task_list_url":"http://www.mapzqq-com.com/data/index",
			#接受任务URL
			"accept_url":"http://www.mapzqq-com.com/data/receive-try",
			#获取运行任务详情URL
			"detail_url":"http://www.mapzqq-com.com/data/run-task",
            "cookie_path": f"cookies/mapzqq_{self.account}.txt",
			#接受任务时失败重试次数
			"accept_retry_count":1,
			#刷任务列表间隔时间最小值
			"refresh_tasklist_delta_min" : 5,
			#刷任务列表间隔时间最大值
			"refresh_tasklist_delta_max" : 300,
			#接受任务最小延迟时间
            "accept_task_min_delay" : 0.5 ,
            #接受任务最大延迟时间
			"accept_task_max_delay" : 1.2,

			"headers":{
				"Host": "www.mapzqq-com.com",
			    "Connection": "keep-alive",
			    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
			    "Referer": "http://www.mapzqq-com.com/static/shubao/activity_v14/index.html",
			}
        }
        return cfg

    def getParams(self):
        param = loads(dumps(self.rst_param))
        param["timestamp"] = self.getTimestamp()

        return param

    def request(self,session,url,taskId=None):
        param = self.getParams()
        if taskId != None:
            param["taskId"] = taskId
        try:
            return session.post(url, data=param, headers=self.headers)
        except:
            pass


    def refreshTaskList(self,session):
        url = self.cfg.get("task_list_url")
        return self.request(session,url)

    def acceptTask(self,session,taskId):
        url = self.cfg.get("accept_url")
        return self.request(session,url,taskId)

    def getTimestamp(self):
        t = "".join(str(time.time()).split("."))
        t = t[0:13]
        return t

    def getRunningTaskInfo(self,session,taskId):
        url = self.cfg.get("detail_url")
        response = self.request(session,url, taskId)
        expire_at = 0
        name = ''
        if response.status_code == 200:
            response = json.loads(response.content)

            err_code = response.get("status")
            if err_code == 1:
                data = response.get("data")
                task = data.get("task")
                if task:
                    # expire_at =  task.get("endTime")
                    expire_at = math.ceil(time.time()+data.get("rest"))
                    name = task.get("name")

        return {
            'expire_at': expire_at,
            'response': response,
            'task':task,
            'taskId': taskId,
            'name':name,
            'err_code':0 if err_code == 1 else err_code
        }