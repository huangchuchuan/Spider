# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.http import Request


class OopImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['pic_url']:
            yield Request(image_url)

    def item_completed(self, results, item, info):
        # results - [(success, image_info_or_failure)] image_info - {url: x, path: x, checksum: x}
        pic_paths = []
        for success, image_info_or_failure in results:
            if success:
                pic_paths.append(image_info_or_failure['path'])
            else:
                pic_paths.append([])
        item['pic_path'] = pic_paths
        return item
