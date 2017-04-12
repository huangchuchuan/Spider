# -*- coding: utf-8 -*-

import scrapy
import json
import traceback
import mymongo
from ZhenAi.items import ZhenaiItem


class ZhenaiSpider(scrapy.Spider):
    name = 'zhenai_spider'
    start_urls = [
        'http://search.zhenai.com/v2/search/getPinterestData.do?'
        'sex=1&agebegin=18&ageend=-1&workcityprovince=-1&workcitycity=-1'
        '&info=&h1=-1&h2=-1&salaryBegin=-1&salaryEnd=-1&occupation=-1&h=-1'
        '&c=-1&workcityprovince1=-1&workcitycity1=-1&constellation=-1&animals=-1'
        '&stock=-1&belief=-1&lvBegin=-1&lvEnd=-1&condition=66&orderby=hpf&hotIndex=&online='
        '&currentpage=2&topSearch=false',
        'http://search.zhenai.com/v2/search/getPinterestData.do?'
        'sex=0&agebegin=18&ageend=-1&workcityprovince=-1&workcitycity=-1'
        '&info=&h1=-1&h2=-1&salaryBegin=-1&salaryEnd=-1&occupation=-1&h=-1'
        '&c=-1&workcityprovince1=-1&workcitycity1=-1&constellation=-1&animals=-1'
        '&stock=-1&belief=-1&lvBegin=-1&lvEnd=-1&condition=66&orderby=hpf&hotIndex=&online='
        '&currentpage=2&topSearch=false',
    ]
    # important! ZhenAi use X-Requested-With and Referer to defend spiders
    myheaders = {
        'Host': 'search.zhenai.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://search.zhenai.com/v2/search/pinterest.do?'
                   'sex=1&agebegin=18&ageend=-1&workcityprovince=-1&workcitycity=-1'
                   '&info=&h1=-1&h2=-1&salaryBegin=-1&salaryEnd=-1&occupation=-1&h=-1'
                   '&c=-1&workcityprovince1=-1&workcitycity1=-1&constellation=-1&animals=-1'
                   '&stock=-1&belief=-1&lvBegin=-1&lvEnd=-1&condition=66&orderby=hpf&hotIndex=&online=',
    }

    def parse(self, response):
        data = {}
        try:
            data = json.dumps(response)
        except:
            traceback.print_exc()
        if data and 'data' in data:
            doc_list = data['data']
            if len(doc_list) > 0:
                mongo = mymongo.MyMongo()
                mongo.insert_doc('ZhenAi', 'SimpleData', doc_list)
                for doc in doc_list:
                    member_id = doc['member_id']
                    url = 'http://album.zhenai.com/u/{}?flag=s'.format(member_id)
                    yield scrapy.Request(url=url, callback='parse_detail', headers=ZhenaiSpider.myheaders)

    def parse_detail(self, response):
        # TODO
        items =
        pass