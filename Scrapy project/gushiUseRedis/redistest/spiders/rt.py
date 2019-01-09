from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider  # 导入RedisCrawlSpider


class Read2Spider(RedisCrawlSpider):  # 继承的父类修改一下
    name = 'rt'  # 爬虫名字
    # start_urls = ['https://www.dushu.com/book/1081.html']  # 初始url

    # 键名称的一般规则  爬虫名字:start_urls
    redis_key = 'rt:start_urls'  # 由主机提供

    # 指定了页面内，链接的提取规则，会被父类自动调用
    rules = (
        Rule(LinkExtractor(allow=r'/book/1081_\d+.html'), callback='parse_item', follow=True),
    )

    # 页面数据解析函数
    # 可以自定义，只要保证callback的参数与这个函数名一致即可
    def parse_item(self, response):
        # 每页的图书列表
        book_list = response.xpath('//div[@class="bookslist"]//li')

        for each in book_list:
            i = {}
            i['title'] = each.xpath('.//h3//@title').extract_first()
            i['img_url'] = each.xpath('.//img/@src').extract_first()

            print(i)
            yield i
