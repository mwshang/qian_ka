import time
from main.common.config import TryplayCfg
from pickle import dumps,loads
import json
from main.common.vo import ResponseData,RunningTaskData


# 钱咖
class Tryplay_QianKaCfg(TryplayCfg):
    def __init__(self,account):
        super().__init__(account)

    def _getCfg(self):
        cfg = {
            'name':'钱咖',
            "TaskList":"main.qianka.tasklist.QianKaTaskList",
            "AcceptTaskAction":"main.qianka.actions.QianKaBatchAcceptTaskAction",
            #刷新任务列表URL
            "task_list_url":"https://qianka.com/s4/lite.subtask.list",
            #接受任务URL
            "accept_url":"https://qianka.com/s4/lite.subtask.start?task_id={0}&quality=0",
            #钱迦获取运行任务详情URL
            "detail_url":"https://qianka.com/s4/lite.subtask.detail?task_id={0}",
            "cookie_path":f"cookies/qianka_{self.account}.txt",
             #领取奖励url
            'get_reward':'https://qianka.com/s4/lite.subtask.checkState?task_id={0}',
            #接受任务时失败重试次数
            "accept_retry_count":1,
            #刷任务列表间隔时间最小值
            "refresh_tasklist_delta_min" : 5,
            #刷任务列表间隔时间最大值
            "refresh_tasklist_delta_max" : 100,
            #接受任务最小延迟时间
            "accept_task_min_delay" : 1 ,
            #接受任务最大延迟时间
			"accept_task_max_delay" : 2,
            # 试玩时长,单位秒
            "tryplay_time": 180,
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
        return self.request(session, url, self.headers)

    def getRunningTaskInfo(self, session, taskId):
        url = self.cfg.get("detail_url")
        url = url.format(taskId)
        response = self.request(session,url,headers=self.headers) #session.get(url, headers=self.headers)

        expire_at = 0
        name = ""
        if response.status_code == 200:
            response = json.loads(response.content)
            err_code = response.get("err_code")
            if err_code == 0:
                payload = response.get("payload")
                expire_at = payload.get("expire_at")
                name = payload.get("app_name")


        return RunningTaskData().fill(expire_at=expire_at, response=response,  taskId=taskId, name=name,
                                 err_code=err_code)

        # 获取奖励

    def getReward(self, session, taskId):
        url = self.cfg.get("get_reward") % taskId
        response = self.request(session, url,self.headers)
        err_code = -1
        if response.get("err_code") == 0:
            payload = response.get("payload")
            if payload.get('status') == 3:#这儿还没有确定
                err_code = 0
                print('领取奖励成功!!!!!')
                # "remain_seconds": 0,
                # "wait_time": 2000,
                # "status": 3
            # response = json.loads(response.content)
            # print(f'领取奖励:{response.get("msg")}')
            # if response.get("status") == 1:
            #     err_code = 0

        rd = ResponseData().fill(err_code=err_code, response=response)
        return rd

