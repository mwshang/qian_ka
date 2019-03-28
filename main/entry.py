from selenium import webdriver
from selenium.webdriver import PhantomJS

headers = {
    "Host":"qianka.com",
    "User-Agent" :	"AdoptingPets/2 CFNetwork/974.2.1 Darwin/18.0.0",
    "Access-Control-Allow-Origin" :	"*",
    "X-QK-AUTH" :	"726A4A57-7910-4297-BD80-3C90CD8064C1|cc3cc990-4ec1-4af8-b5b3-c38eb09bb164|",
    "X-QK-SCHEME" :	"com.haodou.app",
    "X-QK-DSID" :	"658577876",
    "X-QK-TIME" :	"1553339970",
    "X-QK-SIGN" :	"5CFA2E4B59D9668AB0512D5C337A9EBE",
    "X-QK-EXTENSION" :	"12.0|1|121c83f76066335c318",
    "X-QK-PUSH-STATE" :	"0",
    "Access-Control-Allow-Headers" :	"X-Qk-Auth, *",
    "Connection" :	"keep-alive",
    "X-QK-TAG" :	"<b51ee1eb 88f80fa1 6014837e 36a5c79d 1a3e3991 1844139f 42f044de 1557faa1>",
    "X-QK-API-KEY" :	"c26007f41f472932454ea80deabd612c",
    "Accept-Language" :	"zh-cn",
    "X-QK-APPV" :	"iPhone9,1|1556.000000|com.haodou.app|1.1.2",
    "Accept" :	"*/*",
    "Accept-Encoding" :	"br, gzip, deflate"
}

chrome = webdriver.Chrome()
response = chrome.get('http://qianka.com/s5k/key.bootstrap')
print(response.status_code)

