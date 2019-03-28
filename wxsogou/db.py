import redis
import requests
from weixin.config import PROXY_POOL_URL

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'sogoweixin'

class RedisClient(object):
    def __init__(self,host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host,port=port,password=password,decode_responses=True)

    def push(self,snuid):
        """
        从列表头部插入snuid，
        :param snuid: 参数 snuid
        :return: 添加结果
        """
        return self.db.lpush(REDIS_KEY,snuid)

    def pop(self):
        """
        移出并获取列表的最后一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        :return: 尾部的snuid
        """
        return self.db.brpop(REDIS_KEY)

    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.llen(REDIS_KEY)

    def get_proxy(self):
        """
        从代理池获取代理
        :return:
        """
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                print('Get proxy',response.text)
                return response.text
            return None
        except Exception:
            return None

