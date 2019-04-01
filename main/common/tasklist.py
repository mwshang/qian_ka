
import requests
import http.cookiejar as cookielib
import functools

from main.common.actionmanager import ActionManager
from main.common.vo import *
from main.common.actions import *
from main.common.config import *

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

    def setRunningTask(self, task):
        if task.isRunning():
            self.runningTask = task
            self.am.clear()
            action = RunningTaskAction(self, task)
            self.am.addAction(action)
        else:
            logger.warning(f"TaskList::setRunningTask task is not a running,id={task.id}")

    def tick(self,delta):
        self.am.tick(delta)

    def getCfgValue(self,prop):
        return self.cfg.get(prop)

    def hasRunningTask(self):
        return self.runningTask != None

    def refreshTaskList(self):
        return self.cfg.refreshTaskList(self.session)

    def acceptTask(self,taskId):
        return self.cfg.acceptTask(self.session,taskId)

    def getRunningTaskInfo(self,taskId):
        return self.cfg.getRunningTaskInfo(self.session,taskId)

    def refresh(self):
        logger.debug("start refresh task list ..........")
        self.session.cookies.load()
        response = self.refreshTaskList()
        res = self._handleRefreshResponse(response)
        return res

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
            logger.warning(f"_handleRefreshResponse refresh task error, error_code={oks[1]} {oks[2]}--->{self.task_list_url}")
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
