# -*- coding: utf-8 -*-
import scrapy

from scrapy import Request
from urllib.parse import quote
from json import loads
from typing import List
import scrapy_splash
from functools import partial
from baidubaipin import BaidubaipinItem
from baidubaipin.settings import cookies_str
import re
import time
import datetime


def double_quote(s):
    """
    将中文部分进行两次urlencode
    :param s: 要编码的字符串
    :return:
    """
    return quote(quote(s))


def parse_cookies(cookies: str) -> dict:
    """
    将cookies以键值对形式转化成一个字典
    :param cookies: cookies原始字符串
    :return:
    """
    str_list = cookies.split(";")
    result = {}
    for s in str_list:
        split_result = s.split("=", 1)
        result[split_result[0].strip()] = split_result[1].strip()
    return result


def dict2param(dic) -> str:
    """
    将url中的参数字典转化成真实的url
    :param dic: 参数字典
    :return:
    """
    return "&".join(["{}={}".format(k, v) for k, v in dic.items()])


class BdbpSpider(scrapy.Spider):
    name = 'bdbp'
    allowed_domains = ['zhaopin.baidu.com']
    query_url = 'https://zhaopin.baidu.com/szzw'
    COMMON_HEADER = {
        "Host": "zhaopin.baidu.com",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        "DNT": "1",
        "Accept": "*/*",
        "Referer": "https:/zhaopin.baidu.com/quanzhi?query=%E8%BF%90%E8%90%A5%E4%B8%93%E5%91%98%EF%BC%88%E6%88%90%E9%83%BD%EF%BC%89(%E8%B0%B7%E5%B7%9D%E8%81%94%E8%A1%8C%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8)",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    cookies_str = cookies_str
    id_set = set()
    regSpace = re.compile(r'([\s\r\n\t])+')
    offset = datetime.timedelta(-1)
    today_date = datetime.datetime.now()

    def start_requests(self):
        base_url = "https://zhaopin.baidu.com/api/qzasync?query=&pn={pagenum}&city={cityname}&is_adq=1&pcmod=1&token=%3D%3Dgllma2SG7oIallam2lnVZmbimkFa4aW2pZayplo1Wa&rn=10&date={time}"
        city_list = ["北京", "上海", "广州", "天津", "武汉", "沈阳", "哈尔滨", "西安", "南京", "成都", "重庆 大城市；深圳", "杭州", "青岛", "苏州", "太原",
                     "郑州", "济南", "长春", " 合肥",
                     "长沙", "南昌", "无锡", "昆明", "宁波", "福州", "石家庄 较大的城市；南宁", "徐州", "烟台", "唐山", "柳州", "常州", "鞍山", "厦门", "抚顺",
                     "吉林市", "洛阳", "大同", "包头",
                     "大庆", "淄博", "乌鲁木齐", "佛山", "呼和浩特", "齐齐哈尔", "泉州", "西宁", "兰州", "贵阳", "温州"]
        url_list = []
        for city in city_list:
            for page_num in range(0, 101):
                url_list.append(base_url.format(
                    pagenum=page_num,
                    cityname=city,
                    time=(self.today_date + self.offset).strftime("%Y%m%d") + "_" + self.today_date.strftime("%Y%m%d")
                ))
        for url in url_list:
            yield Request(url, headers=self.COMMON_HEADER, cookies=self.cookies_dict, callback=self.parse)

    def parse(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        json_data = loads(response.body)
        all_info: List[dict] = json_data['data']['disp_data']
        detail_page_url_list: List = json_data['data']['urls']
        for info, query_url in zip(all_info, detail_page_url_list):
            item = BaidubaipinItem()
            id = info['rloc']
            if id in self.id_set:  # 已经爬取过
                continue
            else:
                self.id_set.add(id)
                item['id'] = id
                item['link'] = info['url'] if 'url' in info else 'NULL'
                item['post_time'] = info['lastmod']
                item['job_name'] = info['title']
                item['salary'] = info['salary']
                item['place'] = info['city']
                item['job_nature'] = info['type']
                item['experience'] = info['experience']
                item['education'] = info['education']
                item['job_number'] = info['number']
                item['job_kind'] = info['jobsecondclass'] if 'jobsecondclass' in info else 'NULL'
                item['advantage'] = info['ori_welfare']
                item['company_address'] = info['companyaddress'] if 'companyaddress' in info else 'NULL'
                item['hot_score'] = info['hot_score'] if 'hot_score' in info else 'NULL'
                item['job_safety_score'] = info['job_safety_score'] if 'job_safety_score' in info else 'NULL'
                item['company_reputation_score'] = info[
                    'company_reputation_score'] if 'company_reputation_score' in info else 'NULL'
                item['salary_level_score'] = info['salary_level_score'] if 'salary_level_score' in info else 'NULL'
                item['company_name'] = info['officialname']
                item['company_size'] = info['size'] if 'size' in info else 'NULL'
                item['company_nature'] = info['employertype']
                item['company_industry'] = info['first_level_label'] if 'first_level_label' in info else 'NULL'
                # item['company_homepage'] = 'NULL'
                item['job_place'] = item['place']
                yield item
                # 因不能使用Splash 所以只能舍弃掉几个字段
                # get_content_partial = partial(self.get_content_place_splash, item)
                #
                # param_dict = {
                #     'id': query_url,
                #     'query': info['officialname'],
                #     'city': info['city'],
                #     'is_promise': 1,
                # }
                # yield scrapy_splash.SplashRequest(
                #     f'{self.query_url}?{dict2param(param_dict)}',
                #     headers={
                #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                #                       "Chrome/73.0.3683.103 Safari/537.36", },
                #     cookies=self.cookies_dict,
                #     callback=get_content_partial,
                #     dont_filter=True,
                #     args={'images': 0, 'timeout': 3}
                # )

    def get_content_place_splash(self, item, response):
        """
        使用splash渲染过的页面抓取数据
        """
        item['job_content'] = response.xpath("//div[@class='job-detail']/p/text()").extract()
        item['job_content'] = [self.replace_all_n(t) for t in item['job_content']]
        item['job_place'] = response.xpath("//div[@class='job-addr']/p[2]/text()").extract()
        company_page: list = response.xpath('//a[@data-click="{\'click-act\': \'company_more\'}"]/@href').extract()
        yield item if len(company_page) == 0 else scrapy_splash.SplashRequest(
            url="http://zhaopin.baidu.com" + company_page[0],
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/73.0.3683.103 Safari/537.36", },
            cookies=self.cookies_dict,
            callback=partial(self.get_industry_use_splash, item),
            dont_filter=True,
            args={'images': 0, 'timeout': 3}
        )

    def get_industry_use_splash(self, item, response):
        """
        同上
        """
        industry = response.xpath('//div[@class="industry"]/p[1]/text()').extract()
        item['company_industry'] = industry[0] if len(industry) != 0 else item['company_industry']
        homepage = response.xpath("//p[contains(text(),'企业官网')]/a/text()").extract()
        item['company_homepage'] = homepage[0] if len(homepage) != 0 else 'NULL'
        yield item

    @property
    def cookies_dict(self):
        return parse_cookies(self.cookies_str)

    @property
    def cookies_dict_list(self):
        return [{
            'domain': '.zhaopin.baidu.com',  # 此处xxx.com前，需要带点
            'name': k,
            'value': v,
        } for k, v in self.cookies_dict.items()]

    def replace_all_n(self, text):
        # 以防止提取不到
        try:
            rel = re.sub(self.regSpace, "", text)
            return rel
        except TypeError as e:
            return "空"
