# -*- coding: utf-8 -*-
# @Author : Huangcc

import requests
import urllib
from lxml import etree
import re
import datetime
import codecs


class BaiduZhidao():
    search_url = 'https://zhidao.baidu.com/search?word={keyword}&ie=gbk&site=-1&sites=0&date=0&pn=PAGE'
    my_headers = {
        'Host': 'zhidao.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    comment_url = 'https://zhidao.baidu.com/question/{question_id}.html?sort=9&rn=5&pn=PAGE#wgt-answers'

    def __init__(self, keyword):
        self.session = requests.Session()
        self.keyword = keyword
        self.search_url = self.search_url.format(keyword=urllib.quote(keyword.decode('utf-8').encode('gbk')))
        self.question_ids = []
        self.filename = 'baidu_zhidao-comments-%s.csv' % (datetime.datetime.now().strftime('%Y%m%d-%H%M'))

    def set_keyword(self, keyword):
        self.keyword = keyword

    def reset_filename(self):
        self.filename = 'baidu_zhidao-comments-%s.csv' % (datetime.datetime.now().strftime('%Y%m%d-%H%M'))

    @staticmethod
    def extract_question_id(url):
        pattern = '/question/(\d+?)\.'
        result = re.findall(pattern, url)
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def html_filter(html_text):
        html_text = html_text.replace('\n', '').replace('\t', ' ')
        pattern = re.compile(r'<[^>]+>', re.S)
        no_html_text = pattern.sub('', html_text)
        return no_html_text

    def search(self, page=0):
        print '-*- start search with page %d -*-' % (page / 10 + 1)
        resp = self.session.get(url=self.search_url.replace('PAGE', str(page)), headers=self.my_headers)
        if resp.status_code == 200:
            response = etree.HTML(resp.text)
            urls = response.xpath('//a[@class="ti"]/@href')
            self.question_ids.extend(filter(lambda x: True if x else False, map(self.extract_question_id, urls)))

            next_page = response.xpath('//a[@class="pager-next"]/@href')
            if next_page:
                next_page_number = re.findall('&pn=(\d+)$', next_page[0])
                if next_page_number:
                    next_page_number = int(next_page_number[0])
                else:
                    next_page_number = 0
                self.search(page=next_page_number)  # 递归调用直到没有下一页
            else:
                print '=*= end search with page %d =*=' % (page / 10 + 1)
        else:
            print 'Error status code %d in getting search result with page %d' % (resp.status_code, (page / 10 + 1))
            print resp.content

    def print_question_ids(self):
        print self.question_ids

    def find_comments(self):
        total = len(self.question_ids)
        for i, question_id in enumerate(self.question_ids):
            print '|*| start get content from question id %s - %d/%d |*|' % (question_id, i + 1, total)
            url = self.comment_url.format(question_id=question_id)
            self.comment(url)
            print '_*_ end get content from question id %s - %d/%d _*_' % (question_id, i + 1, total)

    def comment(self, url, page=0):
        print ' * start get comments with page %d *' % (page / 5 + 1)
        resp = self.session.get(url.replace('PAGE', str(page)), headers=self.my_headers)
        if resp.status_code != 200:
            print 'Error status code %d in getting comment result with page %d' % (resp.status_code, (page / 5 + 1))
            print resp.content
        else:
            response = etree.HTML(resp.content)
            comment_nodes = response.xpath('//span[@class="con"]')
            comments = []
            for node in comment_nodes:
                print node.xpath('string(.)')
                comments.append(node.xpath('string(.)').strip())
            print ' | get %d comments | ' % len(comments)
            if comments:
                comments = map(self.html_filter, comments)
                with codecs.open(self.filename, 'a', encoding='utf-8') as f:
                    for data in comments:
                        f.write(data + '\n')

            next_page = response.xpath('//a[@class="pager-next"]/@href')
            if next_page:
                next_page_number = re.findall('&pn=(\d+)#', next_page[0])
                if next_page_number:
                    next_page_number = int(next_page_number[0])
                else:
                    next_page_number = 0
                self.comment(url, next_page_number)  # 递归调用直到没有下一页
            else:
                print ' - end get comments with page %d -' % (page / 5 + 1)


if __name__ == '__main__':
    baidu_zhidao = BaiduZhidao('美年大健康')
    baidu_zhidao.search()
    baidu_zhidao.find_comments()
