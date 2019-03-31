
REFRESH_TASK_MIN_DELTA_TIME = 5 # 刷新任务列表最小间隔时间
REFRESH_TASK_MAX_DELTA_TIME = 300 # 刷新任务最大间隔时间

RUN_DELTA = 1

QTY_REWARD_THRESHOLD = 1200

FPS = 12
PER_FRAME_TIME = 1/FPS # 每一帧的时间

REFRESH_TASKLIST_DELTA_MIN = 30 # 刷任务列表间隔时间最小值
REFRESH_TASKLIST_DELTA_MAX = 180 # 刷任务列表间隔时间最大值

ACCEPT_TASK_MIN_DELAY = 1 #接受任务最小延迟时间
ACCEPT_TASK_MAX_DELAY = 5 #接受任务最大延迟时间

COLUMN_NAMES = ["id", "数量", "奖励", "描述"]

DEPDEBUG = True

#钱迦任务列表
QIANKA_SUBTASK_LIST = "https://qianka.com/s4/lite.subtask.list"
#接受任务URL
QIANKA_SUBTASK_START = "https://qianka.com/s4/lite.subtask.start?task_id={0}&quality=0"
#钱迦获取运行任务详情URL
QIANKA_SUBTASK_DETAIL = 'https://qianka.com/s4/lite.subtask.detail?task_id={0}'
QIANKA_ACCEPT_TASK_DELAY = 1 #接受任务的延迟时间
QIANKA_ACCEPT_RETRY_COUNT = 10 #接受任务时失败重试次数



QIANKA_TASK_HEADERS = {
    "Host": "qianka.com",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 version=1.1.2 ",
    "Referer": "https://qianka.com/v4/tasks/lite",
}

TRYPLAY = "qianka"
ACCOUNT  = "15630631006"