# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from gushi.items import GushiItem


class GushiPipeline(object):
    def __init__(self):
        column = ["编号", "诗词名", "内容", "作者", "标签", "年代", "翻译", "赏析", "对应编号"]
        self.f = open("./data.csv", mode="a", encoding="utf-8")
        self.f.writelines("@".join(column) + "\n")
        self.id = 1

    def process_item(self, item: GushiItem, spider):
        data = [str(self.id), item["name"], item["content"], item["author"], item["tag"], item["age"], item["translation"],
                item["Appreciation"], item["code"]]
        self.f.writelines("@".join(data)+"\n")
        self.id += 1
        self.f.flush()
        return item

    def close_spider(self, item):
        self.f.close()
