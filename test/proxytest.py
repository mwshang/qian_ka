import os
import sys
import requests
from bs4 import BeautifulSoup
import io
dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,dir)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

def get_proxy():
    r = requests.get('http://127.0.0.1:5555/random/')
    proxy = BeautifulSoup(r.text,"lxml").get_text()
    return proxy

def urltest():
    r = requests.get('http://mp.weixin.qq.com/s?src=11&timestamp=1552981005&ver=1493&signature=9vm5pTMhLlUwoLF*ZSIQYFp8M68dqk7uHhkpYfQuTRYrdcK6BSVeIQy1*Slq4QSFvEsVcGUHL7R7hY7S-Lbbgt2Mp1jgsYgSt*BfaqK-1yVxXO0J6wPed5YTldVzV7Lt&new=1', verify=False)
    proxy = BeautifulSoup(r.text,"html.parser").get_text()
    file = open("d:/index_cut.html", "w")
    with open("d:/index_cut.html", "w",encoding='utf8') as file:
        file.write(proxy)
    return proxy

def crawl(url,proxy):
    proxies = {'http': 'http://' + proxy,'https':"https://" + proxy}
    r = requests.get(url,proxies=proxies)
    return r.text

def main():
    proxy = get_proxy()
    html = crawl('http://docs.jinkan.org/docs/flask/',proxy)
    print(html)

if __name__ == '__main__':
   print(urltest())