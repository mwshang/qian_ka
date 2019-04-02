import time
from main.common.config import TryplayCfg
from pickle import dumps,loads
import json


# 钱咖
class Tryplay_QianKaCfg(TryplayCfg):
    def __init__(self,account):
        super().__init__(account)

    def _getCfg(self):
        cfg = {
            "TaskList":"main.qianka.tasklist.QianKaTaskList",
            "AcceptTaskAction":"main.qianka.actions.QianKaBatchAcceptTaskAction",
            #刷新任务列表URL
            "task_list_url":"https://qianka.com/s4/lite.subtask.list",
            #接受任务URL
            "accept_url":"https://qianka.com/s4/lite.subtask.start?task_id={0}&quality=0",
            #钱迦获取运行任务详情URL
            "detail_url":"https://qianka.com/s4/lite.subtask.detail?task_id={0}",
            "cookie_path":f"cookies/qianka_{self.account}.txt",
            #接受任务时失败重试次数
            "accept_retry_count":1,
            #刷任务列表间隔时间最小值
            "refresh_tasklist_delta_min" : 5,
            #刷任务列表间隔时间最大值
            "refresh_tasklist_delta_max" : 300,
            #接受任务最小延迟时间
            "accept_task_min_delay" : 0.5 ,
            #接受任务最大延迟时间
			"accept_task_max_delay" : 2,
            "headers":{
                "Host": "qianka.com",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 version=1.1.2 ",
                "Referer": "https://qianka.com/v4/tasks/lite",
            }
        }
        return cfg

    def acceptTask(self,session,taskId):
        url = self.cfg.get("accept_url")
        url = url.format(taskId)
        return session.get(url, headers=self.headers)

    def getRunningTaskInfo(self,session,taskId):
        url = self.cfg.get("detail_url")
        url = url.format(taskId)
        response = session.get(url, headers=self.headers)

        expire_at = 0
        name = "" # TODO
        if response.status_code == 200:
            response = json.loads(response.content)
            err_code = response.get("err_code")
            if err_code == 0:
                payload = response.get("payload")
                expire_at = payload.get("expire_at")

        return {
            'expire_at':expire_at,
            'response':response,
            'taskId':taskId,
            'err_code':err_code,
            'name':name
        }

