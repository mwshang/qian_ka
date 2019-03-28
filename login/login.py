import requests
from lxml import etree

class Login():
    def __init__(self):
        self.headers = {
            'Referer'       : "https://github.com/login",
            "Origin"        : "https://github.com",
            'User-Agent'    : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            'Host'          : "github.com",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.login_url      = "https://github.com/login"
        self.post_url       = "https://github.com/session"
        self.logined_url    = "https://github.com/settings/profile"
        self.session        = requests.Session()

    def token(self):
        response    = self.session.get(self.login_url,headers=self.headers,verify=False)
        selector = etree.HTML(response.text)
        token = selector.xpath("//div//input[2]/@value")
        return token

    def login(self,email,password):
        post_data = {

            'utf8'   : '✓',
            'authenticity_token' : self.token()[1],
            'login' : email,
            'password' : password,
            'commit': 'Sign in'
        }
        response = self.session.post(self.post_url,data=post_data,headers=self.headers)
        if response.status_code == 200:
            self.dynamics(response.text)

        response  = self.session.get(self.logined_url,headers=self.headers)
        if response.status_code == 200:
            self.profile(response.text)

    def dynamics(self,html):
        selector = etree.HTML(html)
        dynamics = selector.xpath("//div[contains(@class,'news')]//div[contains(@class,'js-repos-container')]//ul[contains(@class,'list-style-none')]//li")
        for item in dynamics:
            dynamic = ''.join(item.xpath(".//a[@href]//text()")).strip()
            print(dynamic)

    def profile(self,html):
        selector = etree.HTML(html)
        name = selector.xpath("//input[@id='user_profile_name']/@value")
        email = selector.xpath("//select[@id='user_profile_email']/option[@value!='']/text()")
        print(name,email)



if __name__ == '__main__':
    login = Login()
    login.login("shangmw@163.com","shangmw1985728")