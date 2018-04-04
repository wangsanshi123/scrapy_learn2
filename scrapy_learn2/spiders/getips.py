# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils import request

from scrapy_learn2.items import Ips


class GetipsSpider(scrapy.Spider):
    '''西刺代理 国内ip'''
    name = "getips"

    # url = 'http://www.data5u.com/'
    # url = 'http://www.xicidaili.com'
    url = 'http://www.xicidaili.com/wt/'

    # url = 'https://www.baidu.com/index.php?tn=monline_3_dg'

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers={
            "User-Agent": "	Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0"})

    pass

    def parse(self, response):
        trs = response.xpath(".//table[@id='ip_list']//tr")

        for tr in trs:
            tds = tr.xpath(".//td")
            if tds:
                # print tds[0].xpath("string()").extract_first().strip()
                ip = tds[1].xpath("string()").extract_first().strip()
                port = tds[2].xpath("string()").extract_first().strip()
                # print "ip:", ip
                # print "port:", port
                # print tds[3].xpath("string()").extract_first().strip()
                item = Ips(ip=ip, port=port)
                # yield item
                # print "\n"
        print '======end============'
        pass
