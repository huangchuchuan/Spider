# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OopItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    location = scrapy.Field()
    birth = scrapy.Field()
    tall = scrapy.Field()
    work_city = scrapy.Field()
    born_city = scrapy.Field()
    work = scrapy.Field()
    parent = scrapy.Field()
    only_child = scrapy.Field()
    rich = scrapy.Field()
    interest = scrapy.Field()
    distance_love = scrapy.Field()
    year_married = scrapy.Field()
    num_child = scrapy.Field()
    lowest_command = scrapy.Field()
    special_command = scrapy.Field()
    introduction = scrapy.Field()
    pic_url = scrapy.Field()
    pic_path = scrapy.Field()
    pass
