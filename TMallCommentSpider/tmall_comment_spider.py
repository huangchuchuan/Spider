# -*- coding: utf-8 -*-
# @Author : Huangcc

import urllib
import re
import json
import time
import random
import requests
import codecs
import datetime
from lxml import etree

search_keyword = '美年健康'


class TmallCommentSpider():
    name = 'tmall_comment_spider'
    keyword = urllib.quote(search_keyword.decode('utf-8').encode('gbk'))
    search_url = 'https://list.tmall.com/search_product.htm?q={keyword}&type=p&vmarket=' \
                 '&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton'.format(keyword=keyword)
    item_url = 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.0.0.50092370Go9Qa5' \
               '&s={start_index}&q={keyword}&sort=s&style=g&from=.list.pc_1_searchbutton' \
               '&type=pc#J_Filter'
    comment_url = 'https://rate.tmall.com/list_detail_rate.htm'

    my_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    start_urls = [search_url]

    def __init__(self):
        self.filename = 'tmall-comments-%s.csv' % (datetime.datetime.now().strftime('%Y%m%d-%H%M'))
        self.session = requests.session()
        print self.keyword

    def pre_get(self):
        self.session.get(url='https://www.tmall.com/')

    def start_query(self):
        self.pre_get()
        my_headers = self.my_headers
        my_headers['Host'] = 'list.tmall.com'
        my_headers['Connection'] = 'keep-alive'
        my_headers['Upgrade-Insecure-Requests'] = '1'
        my_headers['Referer'] = 'https://www.tmall.com/'
        for url in self.start_urls:
            resp = self.session.get(url=url, headers=my_headers, allow_redirects=False)
            # resp = self.session.get(url=url, headers=my_headers)
            print resp.url
            print resp.content
            self.parse(resp)

    def parse(self, response):
        response = etree.HTML(response.content)
        total_page_selector = response.xpath('//input[@name="totalPage"]')
        if total_page_selector:
            total_page = total_page_selector[0].get('value')
            for page in range(total_page):
                start_index = page * 60
                page_url = self.item_url.format(start_index=start_index, keyword=self.keyword)
                resp = self.session.get(url=page_url, headers=self.my_headers)
                self.parse_search_result(resp)

    def parse_search_result(self, response):
        response = etree.HTML(response.content)
        item_urls = response.xpath('//p[@class="productStatus"]//a/@href').extract()
        comment_nums = response.xpath('//p[@class="productStatus"]//a/text()').extract()
        for i in range(len(item_urls)):
            if int(comment_nums[i]):
                resp = self.session.get(url='https:' + item_urls[i], headers=self.my_headers)
                self.parse_item(resp)

    def parse_item(self, response):
        resp_text = response.text.replace('\n', '')
        pattern = 'TShop\.Setup\((.*?)\);'
        result = re.findall(pattern, resp_text)

        data = {
            'itemId': '',  # 必填
            'spuId': '',  # 必填
            'sellerId': '',  # 必填
            'order': '3',
            'currentPage': '1',  # 页
            'append': '0',
            'content': '1',
            'tagId': '',
            'posi': '',
            'picture': '',
            'ua': '',
            'needFold': '0',
            '_ksTS': '',  # 毫秒时间戳_四位随机数
            'callback': '',  # jsonp_四位随机数+1
        }

        if result:
            json_data = json.loads(result[0])
            item_do = json_data['itemDO']

            data['itemId'] = item_do['itemId']
            data['spuId'] = item_do['spuId']
            data['sellerId'] = item_do['userId']
            random_int = random.randint(1000, 9998)
            data['_ksTS'] = '%d_%d' % (time.time() * 1000, random_int),  # 毫秒时间戳_四位随机数
            data['callback'] = 'jsonp_%d' % (random_int + 1)

            my_headers = self.my_headers.copy()
            my_headers['Host'] = 'rate.tmall.com'
            my_headers['Referer'] = response.url

            resp = requests.get(self.comment_url, params=data, headers=my_headers)
            json_str = resp.content[len(data['callback']):-1]
            json_data = json.loads(json_str)
            max_pages = json_data['rateDetail']['paginator']['lastPage']
            for i in range(max_pages):
                random_int = random.randint(1000, 9998)
                data['_ksTS'] = '%d_%d' % (time.time() * 1000, random_int),  # 毫秒时间戳_四位随机数
                data['callback'] = 'jsonp_%d' % (random_int + 1)
                data['currentPage'] = str(i + 1)

                resp = self.session.get(url=self.comment_url, params=data, headers=my_headers)
                self.parse_comment(resp)

    def parse_comment(self, response):
        json_data = json.loads(response.text[len('jsonp_9999'):-1])
        rate_list = json_data['rateDetail']['rateList']
        for rate in rate_list:
            user_nickname = rate['displayUserNick']
            user_id = rate['id']
            rate_content = rate['rateContent']
            rate_date = rate['rateDate']

            with codecs.open(self.filename, 'a') as f:
                f.write('|'.join((user_id, user_nickname, rate_content, rate_date)) + '\n')

if __name__ == '__main__':
    tmall = TmallCommentSpider()
    tmall.start_query()
