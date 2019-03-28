import requests
try:
    import cookielib
    print(f"user cookielib in python2.")
except:
    import http.cookiejar as cookielib
    print(f"user cookielib in python3.")

headers = {
    "origin":"https://passport.mafengwo.cn",
    "referer":"https://passport.mafengwo.cn/",
    "user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6726.400 QQBrowser/10.2.2265.400"
}

mafengwoSession = requests.Session()
mafengwoSession.cookies = cookielib.LWPCookieJar(filename="mafengwoCookies.txt")


def mafengwoLogin(account,password):
    print("开始模拟登录马蜂窝")
    postUrl = "https://passport.mafengwo.cn/login/"
    postData = {
        "passport": account,
        "password": password,
    }
    # responseRes = requests.post(postUrl, data=postData, headers=headers)
    responseRes = mafengwoSession.post(postUrl,data=postData,headers=headers)
    # 无论是否登录成功，状态码一般都是 statusCode = 200
    print(f"statusCode = {responseRes.status_code}")
    print(f"text = {responseRes.text}")
    mafengwoSession.cookies.save()

def isLoginStatus():
    routeUrl = "http://www.mafengwo.cn/plan/route.php"
    response = mafengwoSession.get(routeUrl,headers=headers,allow_redirects=False)
    print(f"isLoginStatus={response.status_code}")
    if response.status_code == 200:
        return True
    else:
        return False

if __name__ == '__main__':
    # mafengwoLogin("13439424765","shangmw1985728")
    mafengwoSession.cookies.load()
    isLogin = isLoginStatus()
    print(f"is logined mafengwo = {isLogin}")