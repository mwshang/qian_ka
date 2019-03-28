from requests import Session
from weixin.config import *
from weixin.db import RedisQueue
from weixin.mysql import MySQL
from weixin.request import WeixinRequest
from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
from requests import ReadTimeout, ConnectionError
from pickle import loads,dumps
import time

sct = 11
base_cookie = "SUID=D10F14651F13940A000000005C8DAEEA; SUV=1552789227465177; sw_uuid=3668131517; sg_uuid=4042769286; ssuid=6545735060; IPLOC=CN1100; ld=xZllllllll2t0zE$lllllVh5qiylllllBSy51yllll9lllll9klll5@@@@@@@@@@; ABTEST=3|1552907793|v1; weixinIndexVisited=1; JSESSIONID=aaapE2fNAXwTHb50nM-Lw; ppinf=5|1552908012|1554117612|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTozOnh4eHxjcnQ6MTA6MTU1MjkwODAxMnxyZWZuaWNrOjM6eHh4fHVzZXJpZDo0NDpvOXQybHVQYjZ0VThzLU5lLWpacy1xZ0wxWFJBQHdlaXhpbi5zb2h1LmNvbXw; pprdig=vsba0RP6VlVvFAlRwsqo5t71L1H4k0a9JFovk8Ks5eFg1C4-sXuS7aHZV3geN9O8UMR70R_Gkw7-UDOXv8b5E0CPTNj4c6oenjWx_QQsaFCBpHNmOV3c954WUEBGfEsS4ZMIwjbINMies_G-BmM9uucJB1aJhXVUKL6r2s6cims; sgid=16-30267961-AVyPfuw3gzVGsFqZqZerowA; SNUID=8DF239F2CECA4BB2669B42E2CF0FC745; ppmdig=15530501130000008ca6638dc2d78984138255931ae246ff; sct="
def get_sct():
    global sct
    sct += 1
    return sct
def get_cookie():
    return base_cookie + str(get_sct())


class Spider():
    base_url = 'http://weixin.sogou.com/weixin'
    keyword = 'NBA'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'ABTEST=0|1553070123|v1; SNUID=344B814B7773F2F4278902CD77E51845; IPLOC=CN1100; SUID=423DF73C4631990A000000005C91F82B; SUID=266252D25F20940A000000005C91F82B; JSESSIONID=aaaIO6MIIk4aC_XhZM-Lw; SUV=002F49023CF73D425C91F82BA9EB8957',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    session = Session()
    # session.keep_alive = False
    queue = RedisQueue()
    mysql = MySQL()

    def update_cookie(self):
        self.headers['Cookie'] = get_cookie()

    def get_proxy(self):
        """
        从代理池获取代理
        :return:
        """
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                print('Get Proxy', response.text)
                return response.text
            return None
        except requests.ConnectionError:
            return None

    def start(self):
        """
        初始化工作
        """
        # 全局更新Headers
        # self.update_cookie()
        self.session.headers.update(self.headers)
        start_url = self.base_url + '?' + urlencode({'query': self.keyword, 'type': 2,'sut':7956,'lkt':'1%2C1553052272863%2C1553052272863','s_from':'input','_sug_':'y','sst0':'1553052272967','ie':'utf8','w':'01019900','dr':'1'})
        weixin_request = WeixinRequest(url=start_url, callback=self.parse_index, need_proxy=True)
        # 调度第一个请求
        self.queue.add(weixin_request)

    def parse_index(self, response):
        """
        解析索引页
        :param response: 响应
        :return: 新的响应
        """
        doc = pq(response.text)
        items = doc('.news-box .news-list li .txt-box h3 a').items()
        for item in items:
            url = item.attr('href')
            weixin_request = WeixinRequest(url=url, callback=self.parse_detail)
            yield weixin_request
        next = doc('#sogou_next').attr('href')
        if next:
            url = self.base_url + str(next)
            weixin_request = WeixinRequest(url=url, callback=self.parse_index, need_proxy=True)
            yield weixin_request

    def parse_detail(self, response):
        """
        解析详情页
        :param response: 响应
        :return: 微信公众号文章
        """
        doc = pq(response.text)
        data = {
            'title': doc('.rich_media_title').text(),
            'content': doc('.rich_media_content').text(),
            'date': doc('#post-date').text(),
            'nickname': doc('#js_profile_qrcode > div > strong').text(),
            'wechat': doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        }
        yield data

    def request(self, weixin_request):
        """
        执行请求
        :param weixin_request: 请求
        :return: 响应
        """
        try:
            if weixin_request.need_proxy:
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                        'http': 'http://' + proxy,
                        'https': 'https://' + proxy
                    }
                    return self.session.send(weixin_request.prepare(),
                                             timeout=weixin_request.timeout, allow_redirects=False, proxies=proxies)

            return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False)
            # return self.session.get(weixin_request.url,headers=self.headers,timeout=weixin_request.timeout, allow_redirects=False)
        except (ConnectionError, ReadTimeout) as e:
            print(e.args)
            return None

    def error(self, weixin_request):
        """
        错误处理
        :param weixin_request: 请求
        :return:
        """
        weixin_request.fail_time = weixin_request.fail_time + 1
        print('Request Failed', weixin_request.fail_time, 'Times', weixin_request.url)
        if weixin_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(weixin_request)

    def schedule(self):
        """
        调度请求
        :return:
        """
        while not self.queue.empty():
            # time.sleep(1)
            weixin_request = self.queue.pop()
            callback = weixin_request.callback
            print('Schedule', weixin_request.url)
            response = self.request(weixin_request)

            if response and response.status_code in VALID_STATUSES:
                   self.handleResponse200(response,weixin_request)
                # elif response.status_code in REDIRECT_CODES:
                #     retry_request = loads(dumps(weixin_request))
                #     retry_request.url = response.headers['Location']
                #     r = self.request(retry_request)
                #     if r and r.status_code in VALID_STATUSES:
                #         self.handleResponse200(r, weixin_request)
                #     else:
                #         self.error(weixin_request)
                # else:
                #     self.error(weixin_request)
            else:
                self.error(weixin_request)

    def handleResponse200(self,response,weixin_request):
        callback = weixin_request.callback
        results = list(callback(response))
        if results:
            for result in results:
                print('New Result', type(result))
                if isinstance(result, WeixinRequest):
                    self.queue.add(result)
                if isinstance(result, dict):
                    self.mysql.insert('articles', result)
        else:
            self.error(weixin_request)

    def run(self):
        """
        入口
        :return:
        """
        self.start()
        self.schedule()


if __name__ == '__main__':
    spider = Spider()
    spider.run()