import requests
import http.cookiejar as cookielib

headers = {
    "Host": "qianka.com",
    "Connection": "keep-alive",
    "User-Agent":  "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 version=1.1.2 ",
    "Referer": "https://qianka.com/v4/tasks/lite",
}

session = requests.Session()
session.cookies = cookielib.LWPCookieJar(filename="qianka.txt")
session.cookies.load()

response = session.get("https://qianka.com/s4/lite.subtask.list",headers=headers)
print(response.status_code)
print(response.content)