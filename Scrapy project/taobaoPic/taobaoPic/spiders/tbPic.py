# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy.http import Request
from scrapy.http import FormRequest
import urllib
from selenium import webdriver


class TbpicSpider(scrapy.Spider):
    opt = webdriver.ChromeOptions()
    opt.set_headless()
    driver = webdriver.Chrome()
    key = urllib.request.quote("耳塞")
    offset = 3
    index = 1
    lc = "C:/Users/ggq/Desktop/pic"
    name = 'tbPic'
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"}
    allowed_domains = ['jd.com']

    def start_requests(self):
        return [Request(
            "https://search.jd.com/Search?keyword=%E8%80%B3%E5%A1%9E&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E8%80%B3"
            "%E5%A1%9E&page=1&s=46&click=0",
            headers=self.header, callback=self.next)]

    def parse(self, response):
        data = {
            "TPL_username": "ggqshr1129",
            "TPL_password": "ggq19951129",
            "TPL_redirect_url": "https://s.taobao.com/search?q=%E8%80%B3%E5%A1%9E&commend=all&ssid=s5-e&search_type=mall&sourc"
                                "eId=tb.index&area=c2c&spm=a1z02.1.6856637.d4910789&bcoffset=3&ntoffset=3&p4ppushleft=1%2C48&s=44",
            "um_token": "HV02PAAZ0b080a8b74388cc75bd852e605ad3d1e999999",
            "loginType": "3",
            "J_NcoToken": "e1d856fb69838d2b2d317661ff73ae8663c2f874"}

        return FormRequest.from_response(response,
                                         meta={"cookiejar": response.meta["cookiejar"]},
                                         headers=self.header,
                                         formdata=data,
                                         callback=self.next
                                         )

    def next(self, response):
        self.driver.get(response.url)
        time.sleep(2)
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(5)
        source = self.driver.page_source
        response.replace(body=source)
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        img_list = response.xpath("//img[@data-img='1']/@src").extract()
        img_list += response.xpath("//img[@data-img='1']/@data-lazy-img").extract()
        img_list += response.xpath("//img[@data-img='1']/@source-data-lazy-img").extract()
        print("共下载", img_list.__len__(), "张图片")
        for img in img_list:
            filename = self.lc + "/" + str(self.index) + ".jpg"
            urllib.request.urlretrieve("http:" + img, filename=filename)
            self.index += 1
        uu = "https://search.jd.com/Search?keyword=%E8%80%B3%E5%A1%9E&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E8%80%B3" \
             "%E5%A1%9E&s=46&click=0&page=" + str(self.offset)
        self.offset += 2
        yield Request(uu, headers=self.header, callback=self.next)
