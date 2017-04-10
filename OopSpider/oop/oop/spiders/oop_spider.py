# -*- coding: utf-8 -*-

import scrapy
from oop.items import OopItem
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url


class OopSpider(CrawlSpider):
    name = 'OopSpider'
    allowed_domains = ['date.jobbole.com']
    start_urls = ['http://date.jobbole.com']
    rules = [
        Rule(SgmlLinkExtractor(allow=('/page/\d{,3}/')), follow=True, callback='parse_item')
    ]

    def parse_item(self, response):
        html_selector = scrapy.Selector(response)
        urls = html_selector.xpath('//li[@class="media"]/div/h3/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_detail_item)

    def parse_detail_item(self, response):
        items = OopItem()
        html_selector = scrapy.Selector(response)

        items['url'] = get_base_url(response)

        head_prefix = '//div[@class="p-single"]'
        items['title'] = html_selector.xpath(head_prefix + '//h1/text()').extract()
        items['date'] = html_selector.xpath(head_prefix + '//p[@class="p-meta"]/span[1]/text()').extract()
        items['location'] = html_selector.xpath(head_prefix + '//p[@class="p-meta"]/span[2]/a/text()').extract()

        detail_prefix = '//div[@class="p-entry"]'
        details = html_selector.xpath(detail_prefix + '/p/text()').extract()
        details = map(lambda x: x.replace('\n', ''), details)
        items['birth'] = details[0]
        items['tall'] = details[1]
        items['work_city'] = details[2]
        items['born_city'] = details[3]
        items['work'] = details[4]
        items['parent'] = details[5]
        items['only_child'] = details[6]
        items['rich'] = details[7]
        items['interest'] = details[8]
        items['distance_love'] = details[9]
        items['year_married'] = details[10]
        items['num_child'] = details[11]
        items['lowest_command'] = details[12]
        items['special_command'] = details[13]
        items['introduction'] = details[14]
        items['pic_url'] = html_selector.xpath(detail_prefix + '/p/img/@src').extract()
        return items
