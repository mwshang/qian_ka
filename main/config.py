
REFRESH_TASK_MIN_DELTA_TIME = 5 # 刷新任务列表最小间隔时间
REFRESH_TASK_MAX_DELTA_TIME = 300 # 刷新任务最大间隔时间

RUN_DELTA = 1

QTY_REWARD_THRESHOLD = 1200

FPS = 5
PER_FRAME_TIME = 1/FPS # 每一帧的时间

#钱迦任务列表
QIANKA_SUBTASK_LIST = "https://qianka.com/s4/lite.subtask.list"
#接受任务URL
QIANKA_SUBTASK_START = "https://qianka.com/s4/lite.subtask.start?task_id={0}&quality=0"
#钱迦获取运行任务详情URL
QIANKA_SUBTASK_DETAIL = 'https://qianka.com/s4/lite.subtask.detail?task_id={0}'

QIANKA_TASK_HEADERS = {
    "Host": "qianka.com",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 version=1.1.2 ",
    "Referer": "https://qianka.com/v4/tasks/lite",
}