# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import random


class RedistestPipeline(object):
    def process_item(self, item, spider):
        # 记的要讲item返回，否则在redis数据库中取不到item的值
        return item
