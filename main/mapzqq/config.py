import time
from main.common.config import TryplayCfg
from pickle import dumps,loads
import json
import math
from main.common.vo import ResponseData,RunningTaskData

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
        #领取奖励参数
        self.getreward_param = {
            "sign": "c6be1d08aa7df53c500a4f223088da67",
            "format": "json",
            "customer_id": "20190301zhuniandajiDDDDDc",
            "timestamp": "1554019942178",
            "tryid": 55305,
        }

    def _getCfg(self):
        cfg = {
            'name': '鼠宝',
            "TaskList": "main.mapzqq.tasklist.MapzqqTaskList",#任务列表
            "AcceptTaskAction": "main.mapzqq.actions.MapzqqBatchAcceptTaskAction", #接受任务Action
            #刷新任务列表URL
			"task_list_url":"http://www.mapzqq-com.com/data/index",
			#接受任务URL
			"accept_url":"http://www.mapzqq-com.com/data/receive-try",
			#获取运行任务详情URL
			"detail_url":"http://www.mapzqq-com.com/data/run-task",
            #领取奖励url
            'get_reward':'http://www.mapzqq-com.com/info/receive-reward',
            # cookie文件路径
            "cookie_path": f"cookies/mapzqq_{self.account}.txt",
			#接受任务时失败重试次数
			"accept_retry_count":1,
			#刷任务列表间隔时间最小值
			"refresh_tasklist_delta_min" : 5,
			#刷任务列表间隔时间最大值
			"refresh_tasklist_delta_max" : 300,
			#接受任务最小延迟时间
            "accept_task_min_delay" : 1 ,
            #接受任务最大延迟时间
			"accept_task_max_delay" : 1.2,
            #试玩时长,单位秒
            "tryplay_time":180,

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

    def getRewardParams(self,tryid):
        param = loads(dumps(self.getreward_param))
        param["timestamp"] = self.getTimestamp()
        param['tryid'] = tryid

        return param

    def request(self,session,url,taskId=None,param=None):
        param = self.getParams() if param == None else param
        if taskId != None:
            param["taskId"] = taskId
        try:
            # raise Exception("dd")
            return session.post(url, data=param, headers=self.headers)
        except:
            return ResponseData().fill(status_code=500)

    # 刷新任务列表
    def refreshTaskList(self,session):
        url = self.cfg.get("task_list_url")
        return self.request(session,url)

    # 接受任务
    def acceptTask(self,session,taskId):
        url = self.cfg.get("accept_url")
        return self.request(session,url,taskId)

    def getTimestamp(self):
        t = "".join(str(time.time()).split("."))
        t = t[0:13]
        return t

    # 获取运行任务
    def getRunningTaskInfo(self,session,taskId):
        url = self.cfg.get("detail_url")

        response = self.request(session,url, taskId)
        expire_at = 0
        name = ''
        rid = 0
        if response.status_code == 200:
            response = json.loads(response.content)

            err_code = response.get("status")
            if err_code == 1:
                data = response.get("data")
                rid = data.get('id')
                task = data.get("task")
                if task:
                    # expire_at =  task.get("endTime")
                    expire_at = math.ceil(time.time()+data.get("rest"))
                    name = task.get("name")



        code = 0 if err_code == 1 else err_code
        rst = RunningTaskData().fill(expire_at=expire_at,response=response,task=task,taskId=taskId,name=name,err_code=code)
        rst.rid = rid

        return rst

    # 获取奖励
    def getReward(self,session,taskId):
        param = self.getRewardParams(taskId)
        response = self.request(session,self.cfg.get("get_reward"),param=param)
        err_code = -1
        if response.status_code == 200:
            response = json.loads(response.content)
            print(f'{response.get("msg")}')
            if response.get("status") == 1:
                err_code = 0

        rd = ResponseData().fill(err_code=err_code,response=response)
        return rd