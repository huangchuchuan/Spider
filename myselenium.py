# -*- coding:utf-8 -*-

from selenium import webdriver
import requests
import sqlite3

browser = webdriver.Firefox()
browser.get('http://www.mouser.cn')
html_source = browser.page_source
print html_source

coon = sqlite3.connect('/root/.mozilla/firefox/gmfs2ivm.default/cookies.sqlite')
cursor = coon.cursor()
cursor.execute('select name, value from moz_cookies where baseDomain="mouser.cn"')
cookies = cursor.fetchall()
coon.close()


cookie=[item[0]+"="+item[1]for item in cookies]

cookiestr=';'.join(item for item in cookie)

print cookiestr

myheaders = { 
    'Host': 'www.mouser.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Upgrade-Insecure-Requests': '1',
    'If-None-Match': "76b9f323a7b0ec42447e8435c1bc98bd",
    'Cache-Control': 'max-age=0',
    'Cookie':cookiestr
}

s = requests.session()
#r = s.get('http://www.mouser.cn/Semiconductors/RF-Semiconductors/_/N-96p9c/', headers=myheaders)
r = s.get('http://www.mouser.cn/Semiconductors/RF-Semiconductors/_/N-96p9c/', headers=myheaders)

data = r.content

f = open('data.html', 'w')
f.write(data)
f.close()

browser.close()
