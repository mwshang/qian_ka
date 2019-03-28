from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
import requests
from bs4 import BeautifulSoup

def get_proxy():
    r = requests.get('http://127.0.0.1:5555/random/')
    proxy = BeautifulSoup(r.text,"lxml").get_text()
    return proxy

proxy = get_proxy()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=http://' + proxy)
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser,10)
KEYWORD = 'iPad'

def index_page(page):
    print("正在抓取第",page,'页')
    try:
        url = "https://s.taobao.com/search?q=" + quote(KEYWORD)
        browser.get(url)
        if page > 0:
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager div.form > input')))
            submit = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager div.form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page)
            submit.click()

            wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager li.item.active > span'),str(page)))
            wait.until(EC.presence_of_element_located(By.CSS_SELECTOR,'.m-itemlist .items .item.J_MouserOnverReq  '))
            get_products()
    except TimeoutException:
        index_page(page)
    except Exception:
        index_page(page)

def get_products():
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image' : item.find(".pic .img").attr('data-src'),
            'price' : item.find('.price').text(),
            'title' : item.find("row row-2 title").text(),
            'shop' : item.find(".shop").text(),
            'location' : item.find(".location").text()
        }
        print(product)


index_page(1)




