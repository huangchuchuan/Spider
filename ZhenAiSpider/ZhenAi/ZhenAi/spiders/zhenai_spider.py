# -*- coding: utf-8 -*-

import scrapy
import json
import traceback
import mymongo
from utils import *
from ZhenAi.items import ZhenaiItem
from scrapy.utils.response import get_base_url


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
        items = ZhenaiItem()
        html_selector = scrapy.Selector(response)
        url = get_base_url(response)
        items['url'] = html_selector.xpath(
            '//div[@id="AblumsThumbsListID"]/ul/li/p/img[1]/@data-big-img/text()').extract()

        brief_table_td = html_selector.xpath('//table[@class="brief-table"]/td').extract()  # ['<span>x:</span> y']
        brief_dict = {}
        for td in brief_table_td:
            key, value = get_brief_td_to_key_value(td)
            brief_dict[key] = value

        nick_name = html_selector.xpath('//a[@class="name fs24"]/text()').extract_first()

        id_str = html_selector.xpath('//p[@class="brief-info fs14 lh32 c9f"]/text()').extract_first()
        id = re.findall('ID.*?(\d+)', id_str)[0]

        info = html_selector.xpath(
            '//div[@class="mod-tab-info"]/p[@class="fs14 lh20 c5e slider-area-js"]/text()').extract()
        person_os = re.findall('(.*?)<span', info[0].strip())[0]
        description = re.findall('(.*?)<span', info[1].strip())[0]

        data_table_td = html_selector.xpath('//div[@class="info-floor floor-data posr clearfix"]//table//td').extract()
        data_dict = {}
        for td in data_table_td:
            key, value = get_info_td_to_key_value(td)
            data_dict[key] = value

        life_table_td = html_selector.xpath('//div[@class="info-floor floor-life posr clearfix"]//table//td').extract()
        life_dict = {}
        for td in life_table_td:
            key, value = get_info_td_to_key_value(td)
            life_dict[key] = value

        hobby_table_td = html_selector.xpath('//div[@class="info-floor floor-hobby posr clearfix"]//table//td').extract()
        hobby_dict = {}
        for td in hobby_table_td:
            key, value = get_info_td_to_key_value(td)
            hobby_dict[key] = value

        term_table_td = html_selector.xpath('//div[@class="info-floor floor-term posr clearfix"]//table//td').extract()
        term_dict = {}
        for td in term_table_td:
            key, value = get_info_td_to_key_value(td)
            term_dict[key] = value

        all_data = {
            'nick_name': nick_name,
            'url': url,
            'member_id': id,
            'person_os': person_os,
            'description': description,
            'data': data_dict,
            'life': life_dict,
            'hobby': hobby_dict,
            'term': term_dict,
            'pic_url': items['url']
        }
        mongo = mymongo.MyMongo()
        mongo.insert_doc('ZhenAi', 'CompleteData', all_data)

        return items

