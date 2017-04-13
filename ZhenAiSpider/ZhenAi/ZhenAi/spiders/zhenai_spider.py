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
    # generate all base urls
    base_url = 'http://search.zhenai.com/v2/search/getPinterestData.do?' \
               'sex=%d&agebegin=18&ageend=-1&workcityprovince=-1&workcitycity=-1' \
               '&info=&h1=-1&h2=-1&salaryBegin=-1&salaryEnd=-1&occupation=-1&h=-1' \
               '&c=-1&workcityprovince1=-1&workcitycity1=-1&constellation=-1&animals=-1' \
               '&stock=-1&belief=-1&lvBegin=-1&lvEnd=-1&condition=66&orderby=hpf&hotIndex=&online=' \
               '&currentpage=%d&topSearch=false'
    max_pages = 150
    start_urls = [base_url % (i, j) for i in range(0, 2) for j in range(1, max_pages + 1)]

    def parse(self, response):
        data = {}
        try:
            data = json.loads(response.text)
        except:
            traceback.print_exc()
        if data and 'data' in data:
            doc_list = data['data']
            if len(doc_list) > 0:
                mongo = mymongo.MyMongo()
                mongo.insert_doc('ZhenAi', 'SimpleData', doc_list)
                for doc in doc_list:
                    member_id = doc['memberId']
                    url = 'http://album.zhenai.com/u/{}?flag=s'.format(member_id)
                    yield scrapy.Request(url=url, callback=self.parse_detail)

    def parse_detail(self, response):
        items = ZhenaiItem()
        html_selector = scrapy.Selector(response)
        url = get_base_url(response)
        items['pic_url'] = html_selector.xpath(
            '//div[@id="AblumsThumbsListID"]/ul/li/p/img[1]/@data-big-img').extract()

        honesty_charm = html_selector.xpath('//p[@class="brief-info fs14 lh32 c9f"]/span/span/text()').extract()
        honesty = '--'
        charm = '--'
        if len(honesty_charm) == 2:
            honesty = honesty_charm[0]
            charm = honesty_charm[1]
        zhima_info = html_selector.xpath('//p[@class="brief-name lh32 blue"]/a[6]/text()').extract_first().replace(
            u'\u5206', '')

        brief_table_td = html_selector.xpath(
            '//table[@class="brief-table"]//td').extract()  # ['<td><span>x:</span> y</td>']
        brief_dict = {}
        for td in brief_table_td:
            key, value = get_brief_td_to_key_value(td)
            if key is not None and value is not None:
                brief_dict[key] = value

        nick_name = html_selector.xpath('//a[@class="name fs24"]/text()').extract_first()

        id_str = html_selector.xpath('//p[@class="brief-info fs14 lh32 c9f"]/text()').extract_first()
        id = re.findall('ID.*?(\d+)', id_str)[0]

        person_os = html_selector.xpath(
            '//div[@class="mod-tab-info"]//div[@class="info-item slider info-inner"]'
            '//p[@class="fs14 lh20 c5e slider-area-js"]/text()').extract()

        data_table_td = html_selector.xpath('//div[@class="info-floor floor-data posr clearfix"]//table//td').extract()
        data_dict = {}
        for td in data_table_td:
            key, value = get_info_td_to_key_value(td)
            if key is not None and value is not None:
                data_dict[key] = value

        life_table_td = html_selector.xpath('//div[@class="info-floor floor-life posr clearfix"]//table//td').extract()
        life_dict = {}
        for td in life_table_td:
            key, value = get_info_td_to_key_value(td)
            if key is not None and value is not None:
                life_dict[key] = value

        hobby_table_td = html_selector.xpath(
            '//div[@class="info-floor floor-hobby posr clearfix"]//table//td').extract()
        hobby_dict = {}
        for td in hobby_table_td:
            key, value = get_info_td_to_key_value(td)
            if key is not None and value is not None:
                hobby_dict[key] = value

        term_table_td = html_selector.xpath('//div[@class="info-floor floor-term posr clearfix"]//table//td').extract()
        term_dict = {}
        for td in term_table_td:
            key, value = get_info_td_to_key_value(td)
            if key is not None and value is not None:
                term_dict[key] = value

        all_data = {
            'nick_name': nick_name,
            'url': url,
            'member_id': id,
            'person_os': person_os,
            'honesty': honesty,
            'zhima': zhima_info,
            'charm': charm,
            'data': data_dict,
            'life': life_dict,
            'hobby': hobby_dict,
            'term': term_dict,
            'pic_url': items['pic_url']
        }
        mongo = mymongo.MyMongo()
        mongo.insert_doc('ZhenAi', 'CompleteData', all_data)

        return items
