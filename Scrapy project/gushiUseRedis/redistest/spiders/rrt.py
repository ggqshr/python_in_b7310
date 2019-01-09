# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
import json
from redistest.items import RedistestItem


class RrtSpider(RedisCrawlSpider):
    name = 'rrt'
    redis_key = 'rrt:start_urls'  # 由主机提供
    rules = (
        Rule(LinkExtractor(allow=r'.*'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # 每页的图书列表
        book_list = response.xpath('//div[@class="bookslist"]//li')

        for each in book_list:
            i = RedistestItem()
            i['title'] = each.xpath('.//h3//@title').extract_first()
            i['img_url'] = each.xpath('.//img/@src').extract_first()
            return i
