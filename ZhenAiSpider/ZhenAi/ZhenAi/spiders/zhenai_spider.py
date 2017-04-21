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
    base_url = 'http://search.zhenai.com/v2/search/getPinterestData.do?sex={}&agebegin={}&ageend={}&workcityprovince={}' \
               '&workcitycity={}&education={}' \
               '&occupation={}&info=&marriage={}&h1={}&h2={}&salaryBegin={}&salaryEnd={}' \
               '&h={}&c={}&workcityprovince1={}&workcitycity1={}&constellation={}&animals={}&stock={}&belief={}' \
               '&lvBegin={}&lvEnd={}&condition=66&orderby=hpf&hotIndex=&online={}&currentpage={}&topSearch=false'
    sex = [0, 1]
    agebegin = range(18, 100)
    agebegin.append(-1)
    agebegin.reverse()
    ageend = range(18, 100)
    ageend.append(-1)
    ageend.reverse()
    workcityprovince = [-1]  # TODO
    workcitycity = [-1]  # TODO
    education = range(2, 8)
    education.append(-1)
    education.reverse()
    occupation = range(100, 2900, 100)
    occupation.append(-1)
    occupation.reverse()
    marriage = [-1, 1, 3, 4]  # weihun, liyi, sang'ou
    h1 = range(129, 212)
    h1.append(-1)
    h1.reverse()
    h2 = range(129, 212)
    h2.append(-1)
    h2.reverse()
    salaryBegin = range(103, 109)  # yue shou ru
    salaryBegin.append(-1)
    salaryBegin.reverse()
    salaryEnd = range(103, 109)
    salaryEnd.append(-1)
    salaryEnd.reverse()
    h = range(1, 6)  # house
    h.append(-1)
    h.reverse()
    c = range(1, 6)  # children
    c.append(-1)
    c.reverse()
    workcityprovince1 = [-1]  # TODO
    workcitycity1 = [-1]  # TODO
    constellation = range(1, 13)  # xing zuo
    constellation.append(-1)
    constellation.reverse()
    animals = range(1, 13)  # sheng xiao
    animals.append(-1)
    animals.reverse()
    stock = range(1, 58)  # min zu
    stock.append(-1)
    stock.reverse()
    belief = range(1, 14)  # not sure
    belief.append(-1)
    belief.reverse()
    lvBegin = range(1, 8)
    lvBegin.append(-1)
    lvBegin.reverse()
    lvEnd = range(1, 8)
    lvEnd.append(-1)
    lvEnd.reverse()
    online = [-1, 1]
    currentpage = range(1, 101)
    start_urls = url_generator(base_url, sex, agebegin, ageend, workcityprovince, workcitycity,
                               education, occupation, marriage, h1, h2, salaryBegin, salaryEnd, h, c,
                               workcityprovince1, workcitycity1, constellation, animals, stock, belief, lvBegin, lvEnd,
                               online, currentpage)

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
        zhima_info = html_selector.xpath(
            '//p[@class="brief-name lh32 blue"]//a[@class="flag-credit credit-js"]/text()').extract_first()
        if zhima_info:
            zhima_info = zhima_info.replace(u'\u5206', '')
        if not zhima_info.isdigit():
            zhima_info = '--'

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
            'brief_data': brief_dict,
            'data': data_dict,
            'life': life_dict,
            'hobby': hobby_dict,
            'term': term_dict,
            'pic_url': items['pic_url']
        }
        mongo = mymongo.MyMongo()
        mongo.insert_doc('ZhenAi', 'CompleteData', all_data)

        return items
