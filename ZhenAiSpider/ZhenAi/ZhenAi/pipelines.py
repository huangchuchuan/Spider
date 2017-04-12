# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class ZhenAiImagePipline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['pic_url']:
            yield Request(url)
