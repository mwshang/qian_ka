import requests

from cookiespool.db import RedisClient

conn = RedisClient("accounts","weibo")

def set(account,sep="----"):
	try:
		username, password = account.split(sep)
		result = conn.set(username, password)
		print("帐号", username, "密码", password)
		print("录入成功" if result else "录入失败")
	except ValueError as e:
		print("input error::",e)


def scan():
	 print('请输入账号密码组(如:username----password), 输入exit退出读入')
	 while True:
	 	account = input()
	 	if account == "exit":
	 		break
	 	set(account)

if __name__ == '__main__':
    scan()