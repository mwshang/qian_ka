import requests
import http.cookiejar as cookielib
import time

s = "main.tasklist.MapzqqTaskList"
arr = s.split(".")
sarr = arr[0:len(arr)-1]
print(".".join(sarr))