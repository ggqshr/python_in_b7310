# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
from scrapy.log import logger
import json
import redis as r
from .settings import REDIS_HOST, REDIS_PORT, MONGODB_HOST, MONGODB_PORT
from pymongo import MongoClient


class BaidubaipinPipeline(object):
    def __init__(self):
        self.client = r.Redis(REDIS_HOST, port=REDIS_PORT)
        self.conn = MongoClient(MONGODB_HOST, MONGODB_PORT)
        self.conn.admin.authenticate("ggqshr", "root")
        self.mongo = self.conn.Baidu.Baidu
        # 写入csv要用的
        # self.column = ["id", "link", 'post_time', 'job_name', 'salary', 'place', 'job_nature', 'experience',
        #                'education', 'job_number', 'job_kind', 'advantage', 'job_place', 'company_name',
        #                'company_size', 'company_nature', 'company_industry', 'company_address'
        #     , 'hot_score', 'job_safety_score', 'company_reputation_score', 'salary_level_score']
        # this_file_name = f"{time.strftime('%Y%m%d%H%M', time.localtime(time.time()))}.csv"
        # self.f = open("Baidu" + this_file_name, mode="w", encoding="utf-8")
        # self.f.writelines(",".join(self.column) + "\n")
        # self.f.flush()

    def process_item(self, item, spider):
        count = 0
        if self.client.sadd("id_set", item['id']) == 0:
            return item
        self.mongo.insert_one(dict(item))
        # if len(item) != 0:
        #     result_list = [";".join(item[self.column[index]]) if type(item[self.column[index]]) == list else item[
        #         self.column[index]] for index in range(len(self.column))]
        #     print(",".join(result_list) + "\n")
        #     self.f.writelines(",".join(result_list) + "\n")
        #     count += 1
        # if count == 50:
        #     self.f.flush()
        return item

    def close_spider(self, item):
        logger.info("close spider and close file")
        # self.f.flush()
        # self.f.close()
        self.client.shutdown()
        self.conn.close()
