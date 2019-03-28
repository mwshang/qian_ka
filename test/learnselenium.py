from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time

if False:
    browser = webdriver.Chrome()
    try:
        browser.get("https://www.baidu.com")
        input = browser.find_element_by_id("kw")
        input.send_keys("Python")
        input.send_keys(Keys.ENTER)
        wait = WebDriverWait(browser,10)
        wait.until(EC.presence_of_all_elements_located((By.ID,"content_left")))
        print(browser.current_url)
        print(browser.get_cookies())
        print("---------------")
        print(browser.page_source)
    finally:
        browser.close()

if False:
    browser = webdriver.Chrome()
    browser.get("http://www.runoob.com/try/try.php?filename=jqueryui-api-droppable")
    browser.switch_to.frame("iframeResult")
    source = browser.find_element_by_css_selector("#draggable")
    target = browser.find_element_by_css_selector("#droppable")
    actions = ActionChains(browser)
    actions.drag_and_drop(source,target)
    actions.perform()
    time.sleep(2)
    browser.close()

if False:
    browser = webdriver.Chrome()
    browser.get("https://www.zhihui.com/explore")
    time.sleep(10)
    browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
    time.sleep(2)

    browser.execute_script("alert('To Bottom')")

if False:
    browser = webdriver.Chrome()
    browser.get("http://www.runoob.com/try/try.php?filename=jqueryui-api-droppable")
    browser.switch_to.frame("iframeResult")
    try:
        logo = browser.find_element_by_class_name("logo")
    except NoSuchElementException as e:
        print("NO LOGO")

    browser.switch_to.parent_frame()
    logo = browser.find_element_by_class_name("logo")
    print(logo)
    print(logo.text)

if False:
    browser = webdriver.Chrome()
    browser.get("https://wwww.baidu.com")
    print(browser.get_cookies())
    print(browser.add_cookie({"name":'smw',"pwd":'123','domain':'www.baidu.com','value':'000'}))
    print(browser.get_cookies())
    browser.delete_all_cookies()
    print(browser.get_cookies())

if True:
    browser = webdriver.Chrome()
    browser.get("https://wwww.baidu.com")
    browser.execute_script('window.open()')
    print(browser.window_handles)
    browser.switch_to.window(browser.window_handles[1])
    browser.get("https://www.taobao.com")
    time.sleep(1)
    browser.switch_to.window(browser.window_handles[0])
    browser.get("https://python.org")
