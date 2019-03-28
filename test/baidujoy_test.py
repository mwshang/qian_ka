import requests
import re
from pyquery import PyQuery as pq
import json
from pickle import dumps,loads

page = 1
url = 'http://www.qiushibaike.com/hot/page/' + str(page)
url = 'https://www.qiushibaike.com/hot/page/1/'
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent':user_agent}

try:
    response = requests.get(url,headers=headers)

    content = response.text
    doc = pq(content)
    # print(content)
    # list = doc('.article.block.untagged.mb15.typs_long')
    list = doc('.content-block #content-left').children()
    for item in list.items():

        # thumb = item.find(".thumb")
        # if thumb.length == 0: #图片过滤
        #     continue
        name = item('.author.clearfix a h2').text()
        age = item('.author.clearfix .articleGender.manIcon').text()
        good = item(".stats .stats-vote").text()
        content = item('div a .content span').text()
        comments = item(".stats .stats-comments a").text()


        data = {
            'name': name,
            'age' : age,
            'good' : good,
            'comments' : comments,
            'content' : content
        }
        print('name:{0}\nage:{1}\ngood:{2}\ncontent:{3}\ncomments:{4}\n'.format(name,age,good,content,comments))
except Exception as e:
    print(e.args)
