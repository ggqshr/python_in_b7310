# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaidubaipinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    link = scrapy.Field()  # url
    id = scrapy.Field()  # rloc
    post_time = scrapy.Field()  # lastmod
    job_name = scrapy.Field()  # title
    salary = scrapy.Field()  # salary
    place = scrapy.Field()  # city
    job_nature = scrapy.Field()  # type
    experience = scrapy.Field()  # experience
    education = scrapy.Field()  # education
    job_number = scrapy.Field()  # number
    job_kind = scrapy.Field()  # jobsecondclass
    advantage = scrapy.Field()  # ori_welfare
    company_address = scrapy.Field()  # companyaddress
    company_name = scrapy.Field()  # officialname
    company_size = scrapy.Field()  # size
    company_nature = scrapy.Field()  # employertype
    """
        https://zhaopin.baidu.com/szzw?
        id=http://kg.baidu.com/od/4002/2011615/688ded03ea455ae9d2f3282b868f9a3
        &
        query=运营专员（成都）(谷川联行有限公司)
        &city=成都
        &is_promise=1
        &is_direct=
        &vip_sign=
        &asp_ad_job=
    """
    # job_content = scrapy.Field()  # //div[@class='job-detail']/p/text()
    job_place = scrapy.Field()  # //div[@class='job-addr']/p[2]/text()
    """
    https://zhaopin.baidu.com/api/firmasync?query=谷川联行有限公司&city=四川&qid=51288ea64543cc59&pcmod=1&token=ZaKrqG50jCKmIaFlVaGmnVZmbimkFaYaYiJZau5mu1Wa
    """
    company_industry = scrapy.Field()  # industry
    # company_homepage = scrapy.Field()  # official
    hot_score = scrapy.Field() # 百度对于本条招聘信息的热度评分  hot_score
    job_safety_score = scrapy.Field() # 百度对于招聘信息的安全评分  job_safety_score
    company_reputation_score = scrapy.Field() # 百度对于招聘公司的声誉评分 company_reputation_score
    salary_level_score = scrapy.Field() # 对于薪水评分  salary_level_score

