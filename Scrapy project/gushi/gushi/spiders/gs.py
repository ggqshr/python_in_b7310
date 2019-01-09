# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http.response.html import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from gushi.items import GushiItem
import re
from scrapy.log import logger


class GsSpider(CrawlSpider):
    name = 'gs'
    allowed_domains = ['gushiwen.org']
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--log-level=5')
    # brower = webdriver.Chrome(chrome_options=chrome_options)
    # brower.implicitly_wait(3)
    regSpace = re.compile(r'([\s\r\n\t])+')
    count = 0

    def start_requests(self):
        ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"}
        for i in [Request("https://www.gushiwen.org/shiwen/", headers=ua),
                  Request("https://so.gushiwen.org/authors/", headers=ua),
                  Request("https://www.gushiwen.org/", headers=ua),
                  Request("https://so.gushiwen.org/authors/authorvsw_b90660e3e492A1.aspx", headers=ua), ]:
            yield i

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
        #     self.brower.implicitly_wait(3) # 需要加上隐性等待时间，否则会找不到元素
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
        # 以防止提取不到
        try:
            rel = re.sub(self.regSpace, "", text)
        except TypeError as e:
            return "空"
