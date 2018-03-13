# -*- coding: utf-8 -*-
# @Author : Huangcc

import requests
import json
import re
import base64
import hmac
import hashlib
import time
import datetime
import codecs
from PIL import Image

import sys

reload(sys)
sys.setdefaultencoding("utf-8")


class Zhihu(object):
    sigup_url = 'https://www.zhihu.com/signup'
    home_url = 'https://www.zhihu.com'
    sigin_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    search_url = 'https://www.zhihu.com/search'
    search_api_url = "https://www.zhihu.com/api/v4/search_v3"
    question_page_url = 'https://www.zhihu.com/question/'
    comment_api_url = 'https://www.zhihu.com/api/v4/questions/{question_id}/answers'

    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    authorization = 'oauth ' + client_id

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/64.0.3282.186 Safari/537.36'

    simple_headers = {
        'User-Agent': user_agent,
    }

    headers_sigup = {
        'User-Agent': user_agent,
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'www.zhihu.com'
    }

    headers_sigin = {
        'authorization': authorization,
        'Referer': sigup_url,
        'Origin': home_url,
        'User-Agent': user_agent,
    }

    headers_captcha = {
        'authorization': authorization,
        'Referer': sigup_url,
        'User-Agent': user_agent,
    }

    login_payload = {
        'client_id': client_id,
        'grant_type': 'password',
        'source': 'com.zhihu.web',
        'lang': 'en',
        'ref_source': 'other',
        'utm_source': None,
    }

    search_api_headers = {
        'accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'authorization': 'Bearer 2|1:0|10:1520824661|4:z_c0|92:Mi4xOW43QUF3QUFBQUFBVU1JQkxabUREQ1lBQUFCZ0FsVk5WRC1UV3dEY1hZZzl0QjRxVDFHSmpKbFFCY2NpT0lqVlNR|ae27d5db5fb5be6be4a9e8dcfb871161169b9cd00eb9265341366fbadabffaca',
        # 'Cookie': '_zap=a5e45e29-dbb0-4bcc-b318-23dfca5fd933; q_c1=bf06d2672d984917b2f06efa033cc30f|1505131157000|1502242612000; d_c0="AFDCAS2ZgwyPTmHKenJ488LtpT5Eu0sVI_o=|1507769845"; __utma=51854390.746326380.1507769846.1512042244.1512536288.6; __utmz=51854390.1512536288.6.6.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/41295948; __utmv=51854390.000--|2=registration_date=20161129=1^3=entry_date=20170809=1; q_c1=bf06d2672d984917b2f06efa033cc30f|1520305668000|1502242612000; aliyungf_tc=AQAAAIhMQwyLaQkA7G4Ot+e2JkBHD3BH; _xsrf=23549cd1-24ba-47c3-be8b-cd31a966c66b; capsion_ticket="2|1:0|10:1520824649|14:capsion_ticket|44:NjE3ZGEyYjkzNTIwNDJiNGFjZDdiMjIyMWFhMGYxMjA=|40c554d334082285d04501cd6739f752f3e07145745d495bfcd32c00ebf5d5f1"; z_c0="2|1:0|10:1520824661|4:z_c0|92:Mi4xOW43QUF3QUFBQUFBVU1JQkxabUREQ1lBQUFCZ0FsVk5WRC1UV3dEY1hZZzl0QjRxVDFHSmpKbFFCY2NpT0lqVlNR|ae27d5db5fb5be6be4a9e8dcfb871161169b9cd00eb9265341366fbadabffaca"',
        'Host': 'www.zhihu.com',
        # 'Referer': 'https://www.zhihu.com/search?type=content&q=python',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        'X-API-Version': '3.0.91',
        'X-App-Za': 'OS=Web',
        # 'X-UDID': 'AFDCAS2ZgwyPTmHKenJ488LtpT5Eu0sVI_o=',
    }

    search_api_payload = {
        't': 'general',
        'correction': '1',
        'limit': '10',
        'q': 'python',
        'search_hash_id': '0ca5c03842318b3fdb51cfc4c11340e9',
        'offset': '0'
    }

    comment_api_headers = {
        'accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
    }

    comment_api_payload = {
        'sort_by': 'default',
        'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics',
        'limit': '5',
        'offset': '5',
    }

    def __init__(self, username, password):
        self.username, self.password = username, password
        self.session = requests.session()

    def get_token(self):
        resp = self.session.get(self.sigup_url, headers=self.headers_sigup, allow_redirects=False)
        return resp.cookies['_xsrf']

    def get_captcha(self):
        captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha'
        query_string_parameters = {'lang': 'en'}
        resp = self.session.get(captcha_url, data=query_string_parameters, headers=self.headers_captcha)

        if json.loads(resp.text)['show_captcha']:
            resp = self.session.put(captcha_url, data=query_string_parameters, headers=self.headers_captcha)
            print resp.content
            img_data = base64.b64decode(resp.json()['img_base64'])
            with open('captcha_zhihu.png', 'wb') as f:
                f.write(img_data)

            # 打开验证码
            image = Image.open('captcha_zhihu.png')
            image.show()

            captcha = raw_input(u'请输入验证码：')
            return captcha
        else:
            return None

    def get_signature(self, timestamp):
        h = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_payload['grant_type']
        source = self.login_payload['source']
        h.update(grant_type + self.client_id + source + timestamp)
        return h.hexdigest()

    def check_login(self):
        resp = self.session.get(self.sigup_url, allow_redirects=True, headers=self.simple_headers)
        if resp.url == self.home_url:
            return True

    def login(self):
        xsrf_token = self.get_token()
        timestamp = str(int(time.time() * 1000))
        signature = self.get_signature(timestamp)
        captcha = self.get_captcha()
        self.login_payload.update({
            'username': self.username,
            'password': self.password,
            'timestamp': timestamp,
            'signature': signature,
            'captcha': captcha,
        })
        self.headers_sigin.update({'X-Xsrftoken': xsrf_token})
        resp = self.session.post(self.sigin_url, data=self.login_payload, headers=self.headers_sigin,
                                 allow_redirects=False)
        check = self.check_login()
        if 'error' in resp.text:
            print resp.text
        elif check:
            print u'登陆成功！'

    @staticmethod
    def html_tags_eraser(htmls):
        htmls = str(htmls)
        pattern = re.compile(r'<[^>]+>', re.S)
        return pattern.sub('', htmls).replace('|', ' ').replace('\r', '').replace('\n', '')

    def search_questions(self, keyword):
        # 获取search_hash_id
        search_payload = {
            'type': 'content',
            'q': keyword
        }
        resp = self.session.get(url=self.search_url, params=search_payload, headers=self.simple_headers)
        referer = resp.url

        hash_id = None
        hash_id_pattern = "search_hash_id=([\d\w]+)"
        result = re.search(hash_id_pattern, resp.content)
        if result:
            hash_id = result.group(1)

        # 从cookies获取x-uuid和authorization
        self.session.get(url=self.search_url, params=search_payload, headers=self.simple_headers)
        print self.session.cookies
        x_uuid = self.session.cookies['d_c0'].split('|')[0].replace('"', '')
        authorization = 'Bearer ' + self.session.cookies['z_c0'].replace('"', '')

        self.search_api_headers.update({'authorization': authorization, 'Referer': referer, 'X-UDID': x_uuid})
        print self.search_api_headers

        questions = []
        offset = 0
        limit = 10
        while True:
            print 'Getting search result {} - {}'.format(offset, offset + limit)
            self.search_api_payload.update({'q': keyword, 'search_hash_id': hash_id,
                                            'offset': str(offset), 'limit': str(limit)})
            resp = self.session.get(self.search_api_url, params=self.search_api_payload,
                                    headers=self.search_api_headers)
            json_data = resp.json()

            is_end = json_data['paging']['is_end']
            items = json_data['data']
            # 针对question做特殊过滤
            questions.extend([item['object']['question']['url'].split('/')[-1] for item in items
                              if 'object' in item and 'question' in item['object']])

            if is_end:
                break
            else:
                offset += limit

        return questions

    def get_comments(self, question_ids):
        # 构建输出文件
        filename = 'zhihu-%s-comments.csv' % (datetime.datetime.now().strftime('%Y%m%d-%H%M'))
        # 写入表头
        with codecs.open(filename, 'w', 'utf_8_sig') as f:
            f.write(u'评论id|评论url|评论内容|评论创建时间|评论更新时间|作者|作者url|作者id|问题id|问题标题'
                    u'|问题url|问题创建时间|问题更新时间\r\n')

        limit = 5

        for question_id in question_ids:
            print 'Processing Question {}'.format(question_id)
            question_page_url = self.question_page_url + question_id
            comment_api_url = self.comment_api_url.format(question_id=question_id)
            print comment_api_url

            # 从cookies获取x-uuid和authorization
            self.session.get(url=question_page_url, headers=self.simple_headers)
            print self.session.cookies
            x_uuid = self.session.cookies['d_c0'].split('|')[0].replace('"', '')
            authorization = 'Bearer ' + self.session.cookies['z_c0'].replace('"', '')
            # 组装请求头
            self.comment_api_headers.update({'authorization': authorization, 'Referer': question_page_url,
                                             'X-UDID': x_uuid})
            print self.comment_api_headers

            offset = 0
            while True:
                print 'Getting comment result {} - {}'.format(offset, offset + limit)
                self.comment_api_payload.update({'limit': str(limit), 'offset': str(offset)})
                resp = self.session.get(comment_api_url, params=self.comment_api_payload,
                                        headers=self.comment_api_headers)
                print resp.text
                json_data = resp.json()

                is_end = json_data['paging']['is_end']
                items = json_data['data']

                for item in items:
                    created_time = item['created_time']
                    updated_time = item['updated_time']
                    id_ = item['id']
                    url = item['url']
                    content = item['content']

                    author_name = item['author']['name']
                    author_url = item['author']['url']
                    author_id = item['author']['id']

                    question_title = item['question']['title']
                    question_url = item['question']['url']
                    question_created = item['question']['created']
                    question_updated = item['question']['updated_time']

                    with codecs.open(filename, 'a', 'utf_8_sig') as f:
                        content = '|'.join(
                            map(self.html_tags_eraser, (id_, url, content, created_time, updated_time, author_name,
                                                        author_url, author_id, question_id, question_title,
                                                        question_url,
                                                        question_created, question_updated))) + '\r\n'
                        print content
                        f.write(content)

                if is_end:
                    break
                offset += limit


if __name__ == '__main__':
    zhihu = Zhihu('username', 'password')
    zhihu.login()
    question_ids = zhihu.search_questions('python')
    print len(question_ids)
    print question_ids
    zhihu.get_comments(question_ids)
