import requests
import re
from wxsogou.db import RedisClient
from weixin.config import PROXY_POOL_URL
import time


class SpiderSnuid(object):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': None,
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    url = 'http://weixin.sogou.com/weixin?type=2&s_from=input&query=NBA&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=1325&sst0=1553138442377&lkt=1%2C1553138442273%2C1553138442273'

    def __init__(self):
        self.redis = RedisClient()



    def getHTML(self):
        proxy = self.redis.get_proxy()
        proxies = None
        if proxy:
            proxies = {
                'http':'http://' + proxy,
                'https':'https://' + proxy
            }
            print("正在使用proxy:" + proxy)

        try:
            response = requests.get(self.url,headers=self.headers,allow_redirects=False,proxies=proxies,timeout=30)
            if response.status_code == 200:
                header = response.headers
                print(header)
                snuid = re.findall('(SNUID=.*?;)',header['Set-Cookie'])
                print('snuid:',snuid)
                if len(snuid) != 0:
                    self.redis.push(snuid[0])
                    print('Redis插入:', snuid[0])
            elif response.status_code == 302:
                r = requests.get(response.headers['Location'], headers=self.headers, allow_redirects=False, proxies=proxies,
                                        timeout=30)
                if r.status_code == 200:
                    header = response.headers
                    print(header)
                    snuid = re.findall('(SNUID=.*?;)', header['Set-Cookie'])
                    print('snuid:', snuid)
                    if len(snuid) != 0:
                        self.redis.push(snuid[0])
                        print('Redis插入:', snuid[0])

        except Exception as e:
            print(e.args)

    def run(self):
        while True:
            self.getHTML()

if __name__ == '__main__':
    spider = SpiderSnuid()
    spider.run()