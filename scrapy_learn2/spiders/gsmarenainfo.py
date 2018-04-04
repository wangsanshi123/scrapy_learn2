# -*- coding: utf-8 -*-
import logging
import re
from datetime import datetime, timedelta
from time import strptime, strftime

import scrapy

from scrapy_learn2.items import GsmarenaPhone_info

logger = logging.getLogger(__name__)


class GsmarenainfoSpider(scrapy.Spider):
    name = "gsmarenainfo"
    'https://www.gsmarena.com/vivo_v7-8937.php'

    start_urls = ['https://www.gsmarena.com/vivo_v7-8937.php']

    # brand = "vivo"
    # model = "v7"

    def __init__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.base_url = "http://www.gsmarena.com/"
        pass

    def start_requests(self):
        with open("gsmarenaModelUrls.txt") as f:
            for line in f.readlines():
                infos = line.split(",")
                brand = infos[0]
                model = infos[1]
                url = infos[2]
                yield scrapy.Request(url=url, meta={"brand": brand, "model": model})

    # def parse(self, response):
    #     "（根据指定品牌）分析品牌页面，得到各个型号的入口"
    #     items = response.xpath(".//div[@class='makers']//li")
    #     time = 0
    #     for item in items:
    #         # if time >= 30:
    #         #     logger.info(u"======爬取结束=======")
    #         #     break
    #         #     pass
    #         # if 24 <= time < 30:
    #
    #         # elif time > 32:
    #         #     logger.info(u"======爬取结束=======")
    #         #     break
    #         # time += 1
    #
    #         url = self.base_url + item.xpath(".//a/@href").extract_first()
    #
    #         version = item.xpath(".//span/text()").extract_first()
    #
    #         yield scrapy.Request(url=url, callback=self.parseModel,
    #                              meta={"version": version})
    #     nextPage = response.xpath(".//*[@id='body']/div/div[3]/div[2]/a[2]/@href").extract_first()
    #     if nextPage:
    #         url = self.base_url + nextPage
    #         yield scrapy.Request(url=url, callback=self.parse)
    #     pass
    def parse(self, response):
        "抓取指定型号的概要信息"
        brand = response.meta["brand"]
        model = response.meta["model"]
        network = response.xpath(".//*[@id='specs-list']/table[1]/tbody/tr[1]/td[2]/a/text()").extract_first()
        announced = response.xpath(".//*[@id='specs-list']/table[2]/tbody/tr[1]/td[2]/text()").extract_first()
        announced = self.formatDate(announced)
        available = response.xpath(".//*[@id='specs-list']/table[2]/tbody/tr[2]/td[2]/text()").extract_first()
        "Available. Released 2016, October"

        available = re.sub(r'(.*?[Rr]elease[d ])', '', available)
        available = self.formatDate(available)

        dimensions = response.xpath(".//*[@id='specs-list']/table[3]/tbody/tr[1]/td[2]/text()").extract_first()

        price = response.xpath(
            ".//*[@id='specs-list']/table[12]/tbody/tr[2]/td[2][@data-spec='price']/text()").extract_first()
        price = price if price else "0"

        comment_num = response.xpath(".//*[@id='opinions-total']/b/text()").extract_first()
        url = response.xpath(".//a[@class='button']/@href").extract_first()

        # print("comment_num:", commnent_num)
        yield GsmarenaPhone_info(brand=brand, model=model, network=network,
                                 announced=announced, available=available, dimensions=dimensions,
                                 price=price, comment_num=comment_num, url=url, isContentUpdated=0)

        pass

    def formatDate(self, announced):
        try:
            announced = announced.strip()
            announced = announced.split(" ")
            announced = announced[0] + announced[1] + ",01"
            announced = strptime(announced, "%Y,%B,%d")
            announced = strftime("%Y-%m-%d", announced)
        except:
            try:
                announced = announced + ",01" + ",01"
                announced = strptime(announced, "%Y,%M,%d")
                announced = strftime("%Y-%m-%d", announced)
            except Exception, e:
                return ""
                print e
                pass

            pass
        return announced
