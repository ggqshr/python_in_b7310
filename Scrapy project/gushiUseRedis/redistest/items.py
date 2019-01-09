# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RedistestItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    img_url = scrapy.Field()

class GushiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name=scrapy.Field() # 诗词的名字
    content = scrapy.Field()  # 故事的内容
    author = scrapy.Field() # 作者
    tag = scrapy.Field()  # 标签
    age = scrapy.Field()  # 年代
    translation = scrapy.Field()  # 翻译
    Appreciation = scrapy.Field()  # 赏析
    # flag = scrapy.Field()
    code = scrapy.Field()