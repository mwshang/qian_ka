import http.cookiejar as cookielib
import requests
session = requests.Session()
session.cookies = cookielib.LWPCookieJar(filename="jdcookie.txt")

headers = {
    "Host" : "qianka.com",
    "Referer" :	"https://qianka.com/v4/tasks/lite",
    "Connection" : "keep-alive",
    "User-Agent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 version=1.1.2 bid=com.haodou.app tk=1"
}