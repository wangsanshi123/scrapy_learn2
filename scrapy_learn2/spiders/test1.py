# -*- coding: utf-8 -*-
import scrapy


class Test1Spider(scrapy.Spider):
    name = "test1"
    allowed_domains = ["baidu.com"]
    start_urls = ['http://baidu.com/']

    def parse(self, response):
        print("=======parse==========")

        print response
        pass
