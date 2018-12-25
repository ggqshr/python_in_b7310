#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 功能：抓取商品图片
import re
import urllib
import sys

ua_headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
}
def getPic(k, o):
    baseDir = r'C:\Users\ggq\Desktop\pic'
    keyname = k
    key = urllib.request.quote(keyname)  # 编码
    ii = 0
    offset = o
    for i in range(0, 4):
        url = 'https://s.taobao.com/search?q=' + key + '&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb' \
                                                       '.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8' \
                                                       '&initiative_id=tbindexz_20170306&bcoffset=-9&ntoffset=-9' \
                                                       '&p4ppushleft=1%2C48&s=' + str(
            i * offset)
        request = urllib.request.Request(url,headers = ua_headers)
        data = urllib.request.urlopen(request).read().decode("gbk", "ignore")
        ll = re.findall(r'data-src":"//(.*?)"', data)
        ii += 1
        ss = 0
        for j in ll:
            realUrl = "http://" + j
            file = baseDir + str(ii) + str(ss) + ".jpg"
            ss += 1
            try:
                urllib.urlretrieve(realUrl, file)
                content = "第" + str(ii) + "轮第" + str(ss) + "次爬取成功"
                print(content)
            except Exception as e:
                print(e.message)


if __name__ == "__main__":
    getPic("耳塞", 44)
