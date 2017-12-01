# -*- coding: utf-8 -*-
# @Author : Huangcc

import requests
import time
import shutil
import datetime
import codecs
import re
import random
from PIL import Image
from bs4 import BeautifulSoup


class Zhihu_API:
    index = 'www.zhihu.com'
    default_headers = {
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
    }
    xsrf = None

    def __init__(self, phone, password):
        self.phone = phone
        self.password = password
        self.session = requests.session()
        self.filename = None

    def get_xsrf(self):
        headers = self.default_headers.copy()
        resp = self.session.get('https://' + self.index, headers=headers)
        soup = BeautifulSoup(resp.content, 'lxml')
        self.xsrf = soup.select_one("input[name='_xsrf']").get('value')
        return self.xsrf

    def phone_login(self):
        url = 'https://www.zhihu.com/login/phone_num'
        my_url = 'https://www.zhihu.com/people/hao-qi-hai-bu-si-de-mao-24/activities'
        data = {
            '_xsrf': self.get_xsrf(),
            'captcha_type': 'cn',
            'password': self.password,
            'phone_num': self.phone,
            'remember_me': True,
        }

        headers = self.default_headers.copy()
        headers['Referer'] = 'https://' + self.index
        headers['X-Xsrftoken'] = self.xsrf
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['X-Requested-With'] = 'XMLHttpRequest'

        with open('capture.gif', 'wb') as f:
            resp = self.session.get(
                'https://www.zhihu.com/captcha.gif?r=%d&type=login' % int(time.time() * 1000),
                headers=self.default_headers, stream=True)
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)

        image = Image.open('capture.gif')
        image.show()
        capture = raw_input('Please enter the capture code: ')  #

        data['captcha'] = capture
        self.session.post(url=url, data=data, headers=headers, allow_redirects=False)

        headers = self.default_headers.copy()
        resp = self.session.get(my_url, headers=headers, allow_redirects=False)
        if resp.status_code == 200:
            return True
        else:
            print resp.content
            print resp.status_code
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
                        self.phone_login()

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
    zhihu = Zhihu_API('phone_number', 'password')
    while not zhihu.phone_login():
        pass
    keywords = ['python']
    for keyword in keywords:
        zhihu.search_question(keyword)
