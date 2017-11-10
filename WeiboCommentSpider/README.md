# WeiboCommentSpider
微博评论爬虫

## 工作原理
使用微博登录接口进行模拟登陆获取`cookies`后，在`m.weibo.cn`上进行为所欲为地搜索和评论爬取

## 缺陷
1. 只能取最新的1000条微博搜索结果
2. 串行版
3. 以`无BOM的utf-8`进行编码，得到的csv文件无法在`Microsoft Office Excel`直接打开，建议用`Notepad++`转成`带BOM的utf-8编码`

## 登录api
### 实现
```python
def login(self):
    user = self.get_b64_username()  # 用户名先进行urlencode然后base64编码
    passwd = self.get_rsa_password(self.pubkey, self.nonce, self.servertime)
    self.login_params['su'] = user
    self.login_params['servertime'] = self.servertime
    self.login_params['nonce'] = self.nonce
    self.login_params['rsakv'] = self.rsakv
    self.login_params['sp'] = passwd

    resp = self.session.post(self.login_url, data=self.login_params, headers=self.login_headers)
    if 'retcode%3D0' in resp.content:
        print 'login success'
        return True
    print 'login fail'
    print resp.content
    return False
```
### 原理
先从`https://login.sina.com.cn/sso/prelogin.php`获得加密所需的参数`pubkey`, `servertime`, `nonce`, `rsakv`,
然后对密码进行rsa2加密，js加密代码如下，最后发送到服务器登录接口进行登录
```javascript
var RSAKey = new sinaSSOEncoder.RSAKey();
RSAKey.setPublic(me.rsaPubkey, "10001");
password = RSAKey.encrypt([me.servertime, me.nonce].join("\t") + "\n" + password)
```

## 关于微博和评论api
`m.weibo.cn`是一个神奇的入口，登录使用的是明文的`password`，接口返回的数据是`json`格式，
但是只能获取按时间排序的`1000`条微博。而`weibo.cn`则使用`rsa2`加密的密码，数据加载方式使用令人窒息的`ajax`的动态加载，
返回的数据是`html`/`js`文本。由于时间成本，暂用`m.weibo.cn`入口，后续有需要再继续分析

## 微博api
### headers
```python
self.search_headers = {
    'Host': 'm.weibo.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': '',
}
self.search_referer = 'https://m.weibo.cn/p/100103type%3D2%26q%3D{keyword}?type=wb&queryVal={keyword}' \
                      '&featurecode=20000320&luicode=10000011&lfid=106003type%3D1&title={keyword}'
```
### params
```python
self.search_data = {
    'type': 'wb',
    'queryVal': '{keyword}',
    'featurecode': '20000320',
    'luicode': '10000011',
    'lfid': '106003type=1',
    'title': '{keyword}',
    'containerid': '100103type=2&q={keyword}',
}
```
### response
详见[weibo_search_result_example.json](weibo_search_result_example.json)

## 评论api
### headers
`Referer`校验
```python
self.comment_headers = {
    'Host': 'm.weibo.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    # 'Referer': 'https://m.weibo.cn/status/4172328575544621',
    'Connection': 'keep-alive',
}
```
### params
```python
self.comment_data = {
    'id': '{id}',  # 微博id
    'page': '{page}',  # 第x页
}
```
### response
详见[weibo_comment_result_example.json](weibo_comment_result_example.json)