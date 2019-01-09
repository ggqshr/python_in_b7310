# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re

from redistest.items import GushiItem
from scrapy_redis.spiders import RedisCrawlSpider


# 主要就修改一个这里就行
class GsSpider(RedisCrawlSpider):
    name = 'gs'
    redis_key = 'gs:start_urls'  # 由主机提供
    allowed_domains = ['gushiwen.org']
    regSpace = re.compile(r'([\s\r\n\t])+')
    count = 0

    rules = (
        Rule(LinkExtractor(allow='.*shiwenv_.*'), callback='content_and_other', follow=True),
        Rule(LinkExtractor(allow=""), follow=True),
    )

    def content_and_other(self, response):
        """
        对应古诗词详情页面，下载古诗词的内容和其他信息
        :type response:HtmlResponse
        :param response:
        :return:
        """
        # self.count += 1
        # if self.count % 10000 == 0:
        #     logger.info("brower init !")
        #     self.brower.quit()
        #     self.brower = webdriver.Chrome(chrome_options=self.chrome_options)
        item = GushiItem()
        item["name"] = self.replace_all_n(
            response.xpath(r"/html/body/div[2]/div[1]/div[2]/div[1]/h1/text()").extract_first())
        item["age"] = self.replace_all_n(
            response.xpath(r'/html/body/div[2]/div[1]/div[2]/div[1]/p/a[1]/text()').extract_first())
        item["author"] = self.replace_all_n(
            response.xpath(r'/html/body/div[2]/div[1]/div[2]/div[1]/p/a[2]/text()').extract_first())
        code = re.findall(r'_(.*)\.aspx', response.url)  # 提取对应的编码
        item["code"] = code[0]
        if response.xpath(r'//*[@id="contson{}"]/p'.format(code[0])).extract() == []:
            # 如果没有p标签
            div_content = response.xpath(r'//div[@class="contson"]')[0]
            sj_content = div_content.xpath(r"./text()").extract()
            item["content"] = self.replace_all_n("".join(sj_content))
        else:
            # 如果有p标签
            div_content = response.xpath(r'//div[@class="contson"]')[0]
            sj_content = div_content.xpath(r"./p/text()").extract()
            item["content"] = self.replace_all_n("".join(sj_content))
        item["tag"] = "\t".join(response.xpath(r'/html/body/div[2]/div[1]/div[2]/div[5]//a/text()').extract())
        if len(item["tag"]) == 0:
            item["tag"] = "空"

        # try:
        #     self.brower.get(response.url)
        # except WebDriverException as w:
        #     self.brower.quit()
        #     self.brower = webdriver.Chrome(chrome_options=self.chrome_options)
        #     self.brower.get(response.url)

        # try:
        #     self.brower.find_element_by_xpath(r"//*[contains(@href,'javascript:fanyi')]").click()  # 获取翻译
        #     text = self.brower.find_elements_by_xpath(r'//*[text()="译文"]/parent::*')[1].text
        #     item["translation"] = self.replace_all_n(text)
        # except NoSuchElementException as e:
        #     try:
        #         text = self.brower.find_element_by_xpath(r'//*[text()="译文"]/parent::*').text
        #         item["translation"] = re.sub(self.regSpace, "", text)
        #     except NoSuchElementException as e:
        #         item["translation"] = "空"
        # except IndexError as e:
        #     item["translation"] = "空"
        # except Exception as e:
        #     item["translation"] = "空"

        # try:
        #     self.brower.find_element_by_xpath(
        #         r"//*[text()='赏析']/parent::*/parent::*/parent::*/parent::*//a[text()='展开阅读全文 ∨'] "
        #         r"| //*[ text()='鉴赏']/parent::*/parent::*/parent::*/parent::*//a[text()='展开阅读全文 ∨']").click()
        #     item["Appreciation"] = self.replace_all_n(
        #         self.brower.find_elements_by_xpath(r"//*[text()='赏析' ]/parent::*/parent::*/parent::* | "
        #                                            r"//*[text()='鉴赏']/parent::*/parent::*/parent::*")[
        #             1].text)
        # except NoSuchElementException as e:
        #     item["Appreciation"] = "空"
        # except IndexError as e:
        #     item["Appreciation"] = "空"
        # except Exception as e:
        #     item["Appreciation"] = "空"

        yield item

    def replace_all_n(self, text):
        return re.sub(self.regSpace, "", text)
