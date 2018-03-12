# -*- coding: utf-8 -*-
# @Author : Huangcc

import requests
import time
import datetime
import codecs
import re
import random
import json
import base64
import hashlib
import hmac
from PIL import Image
from bs4 import BeautifulSoup


class Zhihu_API:
    index = 'www.zhihu.com'
    sigup_url = 'https://www.zhihu.com/signup'
    home_url = 'https://www.zhihu.com'
    sigin_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'

    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    authorization = 'oauth ' + client_id

    default_headers = {
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
    }

    headers_sigin = dict(default_headers, **{
        'authorization': authorization,
        'Referer': sigup_url,
        'Origin': home_url,
    })

    headers_captcha = dict(default_headers, **{
        'authorization': authorization,
        'Referer': sigup_url,
    })

    login_payload = {
        'client_id': client_id,
        'grant_type': 'password',
        'source': 'com.zhihu.web',
        'lang': 'en',
        'ref_source': 'other',
        'utm_source': None,
    }

    def __init__(self, phone, password):
        self.phone = phone
        self.password = password
        self.session = requests.session()
        self.filename = None

    def get_token(self):
        resp = self.session.get(self.sigup_url, headers=self.default_headers, allow_redirects=False)
        return resp.cookies['_xsrf']

    def get_captcha(self):
        captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha'
        query_string_parameters = {'lang': 'en'}
        resp = self.session.get(captcha_url, data=query_string_parameters, headers=self.headers_captcha)

        if json.loads(resp.text)['show_captcha']:
            resp = self.session.put(captcha_url, data=query_string_parameters,
                       headers=self.headers_captcha)
            pattern = re.compile(r'"img_base64":"(.+?)=\n"')
            img_base64 = pattern.findall(resp.text)[0]
            img_data = base64.b64decode(img_base64)
            with open('captcha_zhihu.png', 'wb') as f:
                f.write(img_data)

            image = Image.open('captcha_zhihu.png')
            image.show()

            captcha = raw_input('请输入验证码：')
            return captcha
        else:
            return None

    def get_signature(self, timestamp):
        h = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_payload['grant_type']
        source = self.login_payload['source']
        h.update(grant_type + self.client_id + source + timestamp)
        return h.hexdigest()

    def login(self):
        xsrf_token = self.get_token()
        timestamp = str(int(time.time() * 1000))
        signature = self.get_signature(timestamp)
        captcha = self.get_captcha()
        self.login_payload.update({
            'username': self.phone,
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

    def check_login(self):
        resp = self.session.get(self.sigup_url, allow_redirects=True,
                   headers=self.default_headers)
        if resp.url == self.home_url:
            return True
        return False

    def search_question(self, keyword):
        print '-*- searching %s -*-' % keyword
        self.filename = 'zhihu-comments-%s.csv' % (datetime.datetime.now().strftime('%Y%m%d-%H%M'))
        with codecs.open(self.filename, 'a', 'utf-8') as f:
            f.write('|'.join((u'问题url', u'问题标题', u'问题创建时间', u'答人', u'答人主页',
                              u'回答时间', u'回答内容', u'回答评论数')) + '\r\n')

        url = 'https://www.zhihu.com/r/search'
        headers = self.default_headers.copy()
        headers['X-Requested-With'] = 'XMLHttpRequest'
        data = {
            'correction': 1,
            'offset': 0,
            'q': keyword,
            'type': 'content',
        }

        offset = 10

        while True:
            resp = self.session.get(url, params=data, headers=headers)
            json_obj = resp.json()
            htmls = json_obj['htmls']

            for html in htmls:
                soup = BeautifulSoup(html, 'lxml')
                question_uri = soup.select_one("a[class='js-title-link']").get("href")
                print question_uri
                if question_uri and 'question' in question_uri:
                    question_id = question_uri.split('/')[-1]
                    if not self.get_answers_by_id(question_id):
                        self.login()

            # 没有下一页则结束
            if not json_obj['paging']['next']:
                break

            data['offset'] += offset
            time.sleep(random.randint(1, 3))

    def get_answers_by_id(self, question_id):
        question_url = 'https://www.zhihu.com/question/' + question_id
        answers_url = 'https://www.zhihu.com/api/v4/questions/' + question_id + '/answers'
        headers = self.default_headers.copy()
        headers['Referer'] = question_url
        headers['origin'] = "https://www.zhihu.com"

        offset = 20
        data = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,'
                       'annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,'
                       'can_comment,content,editable_content,voteup_count,reshipment_settings,'
                       'comment_permission,created_time,updated_time,review_info,question,excerpt,'
                       'relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;'
                       'data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics',
            'limit': 20,
            'offset': 0,
            'sort_by': 'default'
        }

        self.session.get(question_url, headers=headers)
        headers['x-udid'] = self.session.cookies['d_c0']
        headers['authorization'] = "Bearer Mi4xOW43QUF3QUFBQUFBZ0lMVlZEUzdEQmNBQUFCaEFsVk5QZThMV3dBcjZfTnc3Ml" \
                                   "dKaFo2aTZpN3lFV09Jd2JYUXJ3|1511956797|5ddf0ac6583d4dd338c9a26f979ae8ba8668ba11"
        while True:
            resp = self.session.get(answers_url, params=data, headers=headers)
            json_obj = resp.json()
            if 'error' in json_obj:
                print '!! need authorization  !!'
                return False
            result = json_obj['data']
            if not result:
                print 'question %s ends' % question_id
                return True
            for answer in result:
                question = answer['question']
                question_link = question['url']
                question_title = question['title']
                question_create_time = question['created']

                author = answer['author']
                author_name = author['name']
                author_url = author['url']

                answer_create_time = answer['created_time']
                answer_content = self.html_filter(answer['content'])
                answer_comment_count = answer['comment_count']

                with codecs.open(self.filename, 'a', 'utf-8') as f:
                    f.write('|'.join((question_link, question_title, str(question_create_time), author_name, author_url,
                                      str(answer_create_time), answer_content, str(answer_comment_count))) + '\r\n')

            data['offset'] += offset

            time.sleep(random.randint(1, 3))

    @staticmethod
    def html_filter(html_text):
        html_text = html_text.replace('\n', '').replace('\t', ' ')
        pattern = re.compile(r'<[^>]+>', re.S)
        no_html_text = pattern.sub('', html_text)
        return no_html_text


if __name__ == '__main__':
    zhihu = Zhihu_API('13631252855', 'ibcNqAsysu102')
    zhihu.login()
