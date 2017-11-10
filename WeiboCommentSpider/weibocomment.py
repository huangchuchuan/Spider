# -*- coding: utf-8 -*-
# @Author : Huangcc

import urllib
import base64
import rsa
import binascii
import requests
import time
import json
import datetime
import codecs
from collections import defaultdict

MAX_INT = 999999


class Weibo():
    def __init__(self, user, passwd):
        self.username = user
        self.password = passwd

        self.get_login_params_url = 'https://login.sina.com.cn/sso/prelogin.php'
        self.get_login_params_headers = {
            'Host': 'login.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://weibo.com/login.php',
            'Connection': 'keep-alive',
        }
        self.get_login_params_data = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': '',
            'rsakt': 'mod',
            'client': 'ssologin.js(v1.4.19)',
            '_': '1510196975574',  # 毫秒级别的时间戳
        }

        self.login_params = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': '',
            'vsnf': '1',
            # 'su': 'MTUxMTk5MDQ5NzElNDBzaW5hLmNu',
            'service': 'miniblog',
            # 'servertime': '1510195867',
            # 'nonce': 'P6ZMJ7',
            'pwencode': 'rsa2',
            # 'rsakv': '1330428213',
            # 'sp': '',
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': '210',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
        }
        self.login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        self.login_headers = {
            'Host': 'login.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://weibo.com/login.php',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

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
        self.search_url = 'https://m.weibo.cn/api/container/getIndex'
        self.search_data = {
            'type': 'wb',
            'queryVal': '{keyword}',
            'featurecode': '20000320',
            'luicode': '10000011',
            'lfid': '106003type=1',
            'title': '{keyword}',
            'containerid': '100103type=2&q={keyword}',
        }

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
        self.comment_referer = 'https://m.weibo.cn/status/{weibo_id}'
        self.comment_url = 'https://m.weibo.cn/api/comments/show'
        self.comment_data = {
            'id': '{id}',
            'page': '{page}',
        }

        self.session = requests.session()
        self.servertime = None
        self.nonce = None
        self.pubkey = None
        self.rsakv = None
        self.keyword = None
        self.max_try = 5
        self.weibo_ids = []
        self.csv_seq = '|'

    def get_b64_username(self):
        username = urllib.quote(self.username)
        username = base64.encodestring(username)[:-1]
        return username

    def get_rsa_password(self, pubkey, nonce, server_time):
        # var RSAKey = new sinaSSOEncoder.RSAKey();
        # RSAKey.setPublic(me.rsaPubkey, "10001");
        # password = RSAKey.encrypt([me.servertime, me.nonce].join("\t") + "\n" + password)
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, int("10001", 16))  # 创建公钥
        message = str(server_time) + '\t' + str(nonce) + '\n' + str(self.password)  # 拼接明文js加密文件中得到
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制
        return passwd

    def get_login_params(self):
        self.get_login_params_data['_'] = int(1000 * time.time())
        resp = self.session.get(self.get_login_params_url, params=self.get_login_params_data,
                                headers=self.get_login_params_headers)
        raw_data = resp.content
        raw_data = raw_data[len('sinaSSOController.preloginCallBack('):-1]
        json_data = json.loads(raw_data)
        return json_data['servertime'], json_data['nonce'], json_data['pubkey'], json_data['rsakv']

    def set_login_params(self, servertime, nonce, pubkey, rsakv):
        self.servertime, self.nonce, self.pubkey, self.rsakv = servertime, nonce, pubkey, rsakv

    def login(self):
        user = self.get_b64_username()
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

    def set_search_keyword(self, keyword):
        self.keyword = keyword
        self.search_headers['Referer'] = self.search_referer.format(keyword=urllib.quote(self.keyword))
        self.search_data['queryVal'] = self.search_data['queryVal'].format(keyword=self.keyword)
        self.search_data['title'] = self.search_data['title'].format(keyword=self.keyword)
        self.search_data['containerid'] = self.search_data['containerid'].format(keyword=self.keyword)

    def parse_weibo_response(self, json_data):
        mids = []
        if json_data['cards']:
            cards = json_data['cards'][0]['card_group']
            for card in cards:
                mblog = card['mblog']
                mid = mblog['mid']  # 微博id
                comments_count = mblog['comments_count']  # 评论数量
                if comments_count:
                    mids.append(mid)
                    # text = mblog['text']  # 微博内容，html形式
                    # user = mblog['user']  # 发布者
                    # user_id = user['id']
                    # user_name = user['screen_name']
                    # user_desc = user['description']
        return mids

    def set_max_try(self, n):
        self.max_try = n

    def get_weibo_item_ids(self):
        mids = []
        is_end = False
        page_try = defaultdict(lambda: 0)
        page = 1
        while not is_end:
            self.search_data['page'] = str(page)
            page_try[page] += 1
            if page_try[page] > self.max_try:
                print 'page %d is more than max tries %d' % (page, self.max_try)
                page += 1

            resp = requests.get(self.search_url, params=self.search_data, headers=self.search_headers)
            json_data = {'ok': 0}
            try:
                json_data = resp.json()
            except:
                print resp.content
            if json_data['ok']:
                print 'start page %d' % page
                mids.extend(self.parse_weibo_response(json_data))  # 获取所有带评论的微博id
                if not json_data['cardlistInfo']['page']:
                    is_end = True
                else:
                    page += 1
            else:
                print 'page %d not ok' % page
        print 'getting weibo search result is to be end: %d' % len(mids)
        return mids

    def set_weibo_ids(self, ids):
        self.weibo_ids = ids

    def parse_comment_data(self, json_data):
        comments = []
        if 'data' in json_data and json_data['data']:
            for comment in json_data['data']:
                comment_id = unicode(comment['id'])
                user_id = unicode(comment['user']['id'])
                user_name = unicode(comment['user']['screen_name'])
                comment_content = unicode(comment['text'])
                comments.append((comment_id, user_id, user_name, comment_content))
        return comments

    def curl_comments(self, filename=None):
        # 创建文件并写入表头
        if not filename:
            filename = 'weibo-comments-%s.csv' % (datetime.datetime.now().strftime('%Y%m%d-%H%M'))
        with codecs.open(filename, 'a', 'utf-8') as f:
            f.write(self.csv_seq.join((u'评论id', u'用户id', u'用户名', u'评论')) + '\n')

        current_id_pos = 1
        max_id_pos = len(self.weibo_ids)
        for id_ in self.weibo_ids:
            print '-*- start weibo page %d/%d -*-' % (current_id_pos, max_id_pos)
            current_id_pos += 1

            # 初始化评论页迭代参数
            page = 1
            page_try = defaultdict(lambda: 0)
            comment_headers = self.comment_headers.copy()
            comment_headers['Referer'] = self.comment_referer.format(weibo_id=id_)
            comment_data = self.comment_data.copy()
            comment_data['id'] = id_
            max_page = MAX_INT
            # 抓取评论页
            while page <= max_page:
                # 控制尝试次数，超出最大尝试次数则退出
                page_try[page] += 1
                if page_try[page] > self.max_try:
                    print 'comment page %d/%d is more than max tries %d' % (page, max_page, self.max_try)
                    page += 1
                    # 超出最大页数则退出评论爬取
                    if page > max_page:
                        print 'page %d is more than max_page %d' % (page, max_page)
                        break
                    # 无法获取最大页数则退出评论爬取
                    if page > 1 and max_page == MAX_INT:
                        print 'No next page %d' % page
                        break

                # 开始获取评论
                comment_data['page'] = str(page)
                resp = self.session.get(self.comment_url, params=comment_data, headers=comment_headers)
                json_data = {'ok': 0}
                try:
                    json_data = resp.json()
                except ValueError:
                    # 返回不正确则直接退出评论抓取（接口限制）
                    break
                if json_data['ok']:
                    print 'start comment page %d/%d' % (page, max_page)
                    max_page = min(json_data['max'], max_page)  # 最大评论页数
                    comments = self.parse_comment_data(json_data)  # 获取当前评论页评论
                    with codecs.open(filename, 'a', 'utf-8') as f:
                        for comment in comments:
                            f.write(self.csv_seq.join(comment) + '\n')

                    # 页数控制
                    page += 1
                else:
                    print 'comment page %d/%d not ok' % (page, max_page)


if __name__ == '__main__':
    weibo = Weibo('your_weibo_username', 'your_weibo_password')
    servertime, nonce, pubkey, rsakv = weibo.get_login_params()
    weibo.set_login_params(servertime, nonce, pubkey, rsakv)
    weibo.login()
    weibo.set_search_keyword('冯提莫')
    ids = weibo.get_weibo_item_ids()
    weibo.set_weibo_ids(ids)
    weibo.curl_comments()
