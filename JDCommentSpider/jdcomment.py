# -*- coding: utf-8 -*-
# @Author : Huangcc

import urllib
import requests
import re
import math
import time
import random
import json
import codecs
import datetime
from collections import OrderedDict

KEYWORD = '美年健康'

# code start here
URL_ENCODE_KEYWORD = urllib.quote(KEYWORD)
# 搜索页
SEARCH_REFERER = 'https://search.jd.com/Search?keyword={keyword}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={keyword}&page={page_keyword}&s={start_item}&click=0'
# 搜索结果接口
SEARCH_URL = 'https://search.jd.com/s_new.php'
# 搜索页Host
SEARCH_HOST = 'search.jd.com'
# 评论页
COMMENT_REFERER = 'https://item.jd.com/ID.html'
# 评论结果接口
COMMENT_URL = 'https://sclub.jd.com/comment/productPageComments.action'
# 评论页Host
COMMENT_HOST = 'sclub.jd.com'

CSV_SEQ = '|'  # csv文件分隔符

# replace用的占位符
PAGE_KEYWORD = 'PAGE'
START_ITEM_KEYWORD = 'SS'
COMMENT_REFERER_KEYWORD = 'ID'

# 初始化搜索页的referer
SEARCH_REFERER = SEARCH_REFERER.format(keyword=URL_ENCODE_KEYWORD, page_keyword=PAGE_KEYWORD,
                                       start_item=START_ITEM_KEYWORD)

DEFAULT_REQUEST_HEADERS = {
    # 'Host': 'search.jd.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    # 'Referer': BASE_REFERER,
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

COMMENT_REQUEST_HEADERS = {
    # 'Host': 'sclub.jd.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    # 'Referer': 'https://item.jd.com/12571462129.html',
    'Connection': 'keep-alive',
}

ITEM_REQUEST_HEADERS = {
    'Host': 'item.jd.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'If-Modified-Since': 'Wed, 08 Nov 2017 05:49:40 GMT',
}

DATA = {
    'keyword': KEYWORD,
    'enc': 'utf-8',
    'qrst': '1',
    'rt': '1',
    'stop': '1',
    'vt': '2',
    'wq': KEYWORD,
    'page': '1',
    's': '1',
    'psort': '4',  # 按照评论数排序
    'scrolling': 'y',
    'tpl': '1_M',
    'log_id': '1510033965.96458',
    'show_items': '',
}

COMMENT_DATA = {
    # 'callback': 'fetchJSON_comment98vv152',  # 后面三个数字随机
    # 'productId': '12571462129',  # 商品id
    'score': '0',
    'sortType': '5',
    # 'page': '0',  # 评论第x页
    'pageSize': '10',
    'isShadowSku': '0',
    'fold': '1',
}

COMMENT_EXTRA_KEYWORDS = [
    ('id', u'用户ID'),
    ('nickname', u'用户名'),
    ('content', u'评论内容'),
    ('creationTime', u'评论日期'),
    ('score', u'评分'),
    ('referenceName', u'商品名称'),
    ('productColor', u'产品类型'),
]

COMMENT_EXTRA_KEYWORDS_DICT = OrderedDict()
for key, value in COMMENT_EXTRA_KEYWORDS:
    COMMENT_EXTRA_KEYWORDS_DICT[key] = value


def parse_html_to_get_ids(html_content):
    ids = []
    pattern = '<li data-sku="(\d+)"'  # 正则提取商品id
    results = re.findall(pattern, html_content.replace('\n', '').replace('\t', ''))
    if results:
        ids.extend(results)
    return ids


def get_item_ids():
    # 从搜索页获取商品ids
    ids = []
    session = requests.session()
    resp = session.get(SEARCH_REFERER.replace(PAGE_KEYWORD, '1').replace(START_ITEM_KEYWORD, '1'))
    if resp.status_code == 200:
        one_line = resp.content.replace('\n', '').replace('\t', '')
        pattern = 'LogParm.*?result_count:(.*?),.*?SEARCH.item_count=(.*?);'  # 商品总数，每页显示的数量
        result = re.findall(pattern, one_line)
        if result:
            result_count = float(result[0][0].replace('"', '').replace("'", ''))
            # print result_count
            item_count = int(result[0][1])
            pages = int(math.ceil(result_count / item_count))

            for i in range(pages):
                # 计算奇数页
                page = str(2 * i + 1)
                start_item = str(item_count * i + 1)
                # 封装请求头
                referer_url = SEARCH_REFERER.replace(PAGE_KEYWORD, page).replace(START_ITEM_KEYWORD, start_item)
                headers = DEFAULT_REQUEST_HEADERS.copy()
                headers['Host'] = SEARCH_HOST
                headers['Referer'] = referer_url
                # 构造请求商品列表的数据
                data = DATA.copy()
                data['page'] = page
                data['s'] = start_item
                # 请求奇数页的数据
                resp = session.get(SEARCH_URL, params=data, headers=headers, allow_redirects=False)
                if resp.status_code == 200:
                    odd_ids = parse_html_to_get_ids(resp.content)
                    ids.extend(odd_ids)
                    # 请求偶数页的数据
                    # # 构造请求商品列表的数据：通过show_items把奇数页的id组成的字符串传过去获取剩余部分
                    data['page'] = str(int(page) + 1)
                    data['s'] = str(int(start_item) + item_count)
                    data['show_items'] = ','.join(odd_ids)
                    # # 开始请求偶数页数据
                    resp = session.get(SEARCH_URL, params=data, headers=headers, allow_redirects=False)
                    if resp.status_code == 200:
                        even_ids = parse_html_to_get_ids(resp.content)
                        ids.extend(even_ids)
    return ids


def curl_comments(ids):
    # 构建输出文件
    filename = '%s-comments.csv' % (datetime.datetime.now().strftime('%Y%m%d-%H%M'))
    # 写入表头
    with codecs.open(filename, 'wb', 'GBK') as f:
        f.write(CSV_SEQ.join(COMMENT_EXTRA_KEYWORDS_DICT.itervalues()) + u'\n')

    # 构建请求头
    comment_headers = COMMENT_REQUEST_HEADERS.copy()
    comment_headers['Host'] = 'sclub.jd.com'

    session = requests.Session()
    for id_ in ids:
        comment_headers['Referer'] = COMMENT_REFERER.replace(COMMENT_REFERER_KEYWORD, id_)
        # 构造请求数据
        data = COMMENT_DATA.copy()
        data['callback'] = 'fetchJSON_comment98vv' + str(random.randint(100, 999))
        data['productId'] = id_
        data['page'] = '0'
        # 请求第一页评论获得总页数
        resp = session.get(COMMENT_URL, params=data, headers=comment_headers)
        if resp.status_code == 200:
            resp.encoding = 'utf-8'
            raw_data = resp.text
            raw_data = raw_data[len('fetchJSON_comment98vv152('):-2]  # 去掉前一部分和后面一部分来得到json字符串
            json_data = json.loads(raw_data)
            max_pages = json_data['maxPage']
            # 请求所有评论页
            for i in range(max_pages):
                data['page'] = str(i)
                resp = session.get(COMMENT_URL, params=data, headers=comment_headers)
                if resp.status_code == 200:
                    raw_data = resp.content.decode(resp.encoding, errors='ignore')  # 忽略无法解析的字符
                    raw_data = raw_data[len('fetchJSON_comment98vv152('):-2]  # 去掉前一部分和后面一部分来得到json字符串
                    json_data = json.loads(raw_data)
                    comment_list = json_data['comments']

                    with codecs.open(filename, 'a', 'GBK') as f:
                        for comment in comment_list:
                            result_list = [unicode(comment[key]).replace('\n', '') if key in comment else "" for key in
                                           COMMENT_EXTRA_KEYWORDS_DICT]
                            f.write(CSV_SEQ.join(result_list) + '\n')


if __name__ == '__main__':
    t = time.time()
    good_ids = get_item_ids()
    curl_comments(good_ids)
    print time.time() - t
