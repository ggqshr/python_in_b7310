# -*- coding: utf-8 -*-
from scrapy.log import INFO

# Scrapy settings for baidubaipin project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'baidubaipin'

SPIDER_MODULES = ['baidubaipin.spiders']
NEWSPIDER_MODULE = 'baidubaipin.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    'baidubaipin.middlewares.BaidubaipinSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'baidubaipin.pipelines.BaidubaipinPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

LOG_LEVEL = INFO
# splash的地址，因为百度百聘有些页面是用js加载数据的，不渲染页面是无法爬取到的，所以要用到渲染引擎
SPLASH_URL = 'http://116.56.140.202:8050'
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# 要使用的cookies，因为百度百聘需要登陆后才能爬取
cookies_str = r'BAIDUID=696586132F6F4145E937628826CE64A4:FG=1; BIDUPSID=696586132F6F4145E937628826CE64A4; PSTM=1553757127; BDUSS=dhfmJWNXdXcHlRQll0SEFtfjAtaVE3NHlLV2QtdVRIbjJ5NnBWN1lkVWxpTTljSVFBQUFBJCQAAAAAAAAAAAEAAAA32L9Ruf65~mdncwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACX7p1wl-6dcUD; BDRCVFR[mkUqnUt8juD]=mk3SLVN4HKm; delPer=0; H_PS_PSSID=1422_21093_20883_28771_28723_28838_28584_28604_28892_22158; Hm_lvt_da3258e243c3132f66f0f3c247b48473=1556415844,1556416244,1556416249,1556416292; Hm_lpvt_da3258e243c3132f66f0f3c247b48473=1556416292; PSINO=7; Hm_lvt_4b55f5db1b521481b884efb1078a89cc=1556424416; Hm_lpvt_4b55f5db1b521481b884efb1078a89cc=1556424433'
REDIS_HOST = "116.56.140.202"
REDIS_PORT = 6379

MONGODB_HOST = "116.56.140.202"
MONGODB_PORT = 27017
