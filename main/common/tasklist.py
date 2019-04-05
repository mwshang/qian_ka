
import requests
import http.cookiejar as cookielib
import functools

from main.common.actionmanager import ActionManager
from main.common.vo import *
from main.common.actions import RunningTaskAction,RefreshTaskList
from main.common.config import *
from main.gui.gui import RefreshCookieView
from main.common.constants import *

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskList(object):# 任务列表基类
    def __init__(self,cfg):
        self.cfg = cfg
        # 刷新任务列表请求
        self.task_list_url = cfg.get("task_list_url")
        # 接受任务的URL
        self.accept_url = cfg.get("accept_url")
        # 任务详情URL
        self.task_detail_url = cfg.get("detail_url")
        # cookie文件名路径
        self.cookie_path = cfg.get("cookie_path")

        self.headers = cfg.get("headers")
        self.session = None

        # 正在进行的任务
        self.runningTask = None
        # 标准任务
        self.stdTasks = []
        # 预告任务
        self.incomingTasks = []
        # 预告开始时间 key=开始时间,值为任务ID数组
        self.incomingStartDates = {}
        # 预告任务监听器
        self.incomingListeners = []
        self.am = ActionManager()
        self.am.start()


        if self.session == None:
            self._initSession()

        self.am.addGlobalAction(RefreshTaskList(self))


    def _initSession(self):
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(filename=self.cookie_path)


    def tick(self,delta):
        self.am.tick(delta)

    def getCfgValue(self,prop):
        return self.cfg.get(prop)

    def refreshTaskList(self):
        return self.cfg.refreshTaskList(self.session)

    def acceptTask(self,taskId):
        return self.cfg.acceptTask(self.session,taskId)

    def hasRunningTask(self):
        # action =  self.am.findActionByClass(RunningTaskAction)
        # if action and not action.isFinished():
        #     return True
        # return False
        return self.runningTask != None

    def clearRunningTask(self):
        self.runningTask = None

    def setRunningTask(self, task):
        if task:
            self.runningTask = task
            self.am.clear()
            response = self.getRunningTaskInfo(task.id)
            if response.err_code == 0:
                # response.task.setRuningStatus()
                global observer
                observer.send(MSG_ACCEPTED_ATASK, response)

    def getRunningTaskInfo(self,taskId):
        return self.cfg.getRunningTaskInfo(self.session,taskId)

    def getReward(self):
        return self.cfg.getReward(self.session)

    def refresh(self):
        logger.debug("start refresh task list ..........")
        self.session.cookies.load()
        response = self.refreshTaskList()
        if response.status_code == 200:
            self._handleRefreshResponse(response)

    def resetRefresh(self):
        rtAction = self.am.findGlobalActionByName("RefreshTaskList")
        if rtAction:
            rtAction.reset()

    def _handleRefreshResponse(self,response):
        response = json.loads(response.content)
        oks = self._responseIsSuccess(response)
        if oks[0]:
            # 标准任务
            stdTasks = self._getStdTasksByResponse(response)
            self._initStdTasks(stdTasks,response)
            # 预告任务
            incomingTasks = self._getIncomingTasksByResponse(response)
            self._initIncomingTasks(incomingTasks)
            # 添加预告任务定时器
            self._setIncomingListeners()
        else:
            logger.warning(f"_handleRefreshResponse refresh task error, err_code={oks[1]} {oks[2]}--->{self.task_list_url}")
            # RefreshCookieView(self.session).Show()

            observer.send(MSG_UPDATE_TILELIST_STATUS,{'msg':f'请求失败,请刷新Cookie!!!'})
        return response
    def _responseIsSuccess(self,response):
        err_code = response.get("err_code")
        return (err_code == 0,err_code,response.get("err_msg"))

    # 获取返回中的标准任务
    def _getStdTasksByResponse(self,response):
        pass

    # 获取返回中的预告任务
    def _getIncomingTasksByResponse(self,response):
        pass

    # 初始化标准任务
    def _initStdTasks(self,tasks,response):
        pass

    # 初始化预告任务
    def _initIncomingTasks(self, tasks):
        pass

    # 添加预告任务定时器
    def _setIncomingListeners(self):
        self._clearIncomingListeners()

    def _clearIncomingListeners(self):
        for k in self.incomingListeners:
            k['timer'].cancel()

        self.incomingListeners = []
