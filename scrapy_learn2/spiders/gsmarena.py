# -*- coding: utf-8 -*-
import re
from time import strftime, strptime

import logging
import scrapy
from datetime import datetime, timedelta

from scrapy.utils.response import get_base_url

from scrapy_learn2.items import GsmarenaPhone

logger = logging.getLogger(__name__)


class GsmarenaSpider(scrapy.Spider):
    name = "gsmarena"
    allowed_domains = ["gsmarena.com"]
    # start_urls = ['http://www.gsmarena.com/makers.php3']

    time1 = 0
    time2 = 0
    baseurl_total = "http://www.gsmarena.com/"
    quoteUrl_base = "http://www.gsmarena.com/comment.php3?idType=1&idComment="

    def start_requests(self):
        url = "http://www.gsmarena.com/huawei-phones-58.php"
        brand = "Huawei"
        yield scrapy.Request(url=url, callback=self.parseBrand, meta={"brand": brand})

    def parse(self, response):
        trs = response.xpath(".//div[@class='st-text']/table//tr")

        for tr in trs:
            tds = tr.xpath(".//td")
            # if self.time1 > 0:
            #     break
            for td in tds:
                # if self.time2 > 0:
                #     break
                url = self.baseurl_total + td.xpath(".//a/@href").extract_first()
                # url = "http://www.gsmarena.com/huawei-phones-58.php"
                self.time2 += 1
                brand = td.xpath(".//a/text()").extract_first()
                # brand = "Huawei"
                # print "=======brand==========", brand
                yield scrapy.Request(url=url, callback=self.parseBrand, meta={"brand": brand},
                                     )
            self.time1 += 1
        pass

    def parseBrand(self, response):
        "（根据指定品牌）分析品牌页面，得到各个型号的信息"
        # print "parseBrand"
        # "http://www.gsmarena.com/acer_iconia_talk_s-8306.php"

        items = response.xpath(".//div[@class='makers']//li")
        time = 0
        # print "====len(urls)====", len(items)
        brand = response.meta["brand"]
        for item in items:
            # if time > 0:
            #     break
            # print "url", self.baseurl_total + url.xpath(".//a/@href").extract_first()
            url = self.baseurl_total + item.xpath(".//a/@href").extract_first()
            # print url

            version = item.xpath(".//span/text()").extract_first()

            yield scrapy.Request(url=url, callback=self.parseVersion,
                                 meta={"brand": brand, "version": version})
            time += 1
        pass

    def parseVersion(self, response):
        # print "parseVersion"

        url = response.xpath(".//a[@class='button']/@href").extract_first()
        try:
            url = self.baseurl_total + url
            # print "===parseVersion====", url
            yield scrapy.Request(url=url, callback=self.parseVersion_deep,
                                 meta={"version": response.meta["version"], "brand": response.meta["brand"]})
        except Exception, e:
            logger.error(e)
            pass

        pass

    def parseVersion_deep(self, response):
        # print "parseVersion_deep"
        # divs = response.xpath(".//div[@class='all-opinions']")
        divs = response.xpath(".//div[@class='user-thread']")
        # print len(divs)
        version = response.meta["version"]
        brand = response.meta["brand"]
        for div in divs:
            author = div.xpath(".//li[@class='uname2']/text()").extract_first()
            if not author:
                author = div.xpath(".//li[@class='uname']//b/text()").extract_first()
            location = div.xpath(".//span[@title='Encoded location']/text()").extract_first()
            date = div.xpath(".//li[@class='upost']/time/text()").extract_first()
            if "," in date:
                date = str(date.split(",")[1:])
            try:
                date = strftime("%Y-%m-%d", strptime(date, "%d %b %Y"))
            except Exception, e:
                logger.info(e)
                date = self.parseDate(date)
                pass

            quote_temp = div.xpath(".//p[@class='uopin']/span")
            quote_partial = quote_temp.xpath("string()").extract_first()
            # quote_date = div.xpath(".//a[@class='uinreply']/text()").extract_first()
            quote_date = div.xpath(".//*[@class='uinreply']/text()").extract_first()

            content = div.xpath(".//p[@class='uopin']")
            content = content.xpath("string()").extract_first()
            # print "author:", author
            # print "location:", location
            # print "date:", date

            if quote_temp:
                quote_data_temp = quote_date.split(",")
                quote_author = quote_data_temp[0]
                quote_date = quote_data_temp[1]

                try:
                    content_filter = (quote_author + "," + quote_date + quote_partial).strip()
                    content = content.replace(content_filter, "")

                except Exception, e:
                    logger.error(e)
                    pass
                try:
                    quote_date = strftime("%Y-%m-%d", strptime(quote_date.strip(), "%d %b %Y"))
                except Exception, e:
                    logger.info(e)
                    quote_date = self.parseDate(quote_date)

                    pass
                quote_url = div.xpath(".//span[@class='uinreply-msg']/a/@href").extract_first()
                if not quote_url:
                    quote = div.xpath(".//span[@class='uinreply-msg uinreply-msg-single']/text()").extract_first()

                    yield GsmarenaPhone(brand=brand, version=version, author=author, location=location, date=date,
                                        content=content,
                                        quote_author=quote_author, quote_date=quote_date, quote=quote)

                else:
                    quote_url = self.quoteUrl_base + quote_url.replace("#", "")
                    yield scrapy.Request(url=quote_url, callback=self.parseQuote,
                                         meta={"brand": brand, "version": version, "author": author,
                                               "location": location,
                                               "date": date, "content": content,
                                               "quote_author": quote_author, "quote_date": quote_date,
                                               "url": quote_url},
                                         )

            else:
                yield GsmarenaPhone(brand=brand, version=version, author=author, location=location, date=date,
                                    content=content,
                                    quote_author='', quote_date='', quote='')

                # print "content:", content
                # print "\n"
        nextPage = response.xpath(".//a[@title='Next page']/@href").extract_first()
        if nextPage:
            url = self.baseurl_total + nextPage
            # print "========nextPage========nextPage[0]", nextPage
            # print "========nextPage========url", url
            yield scrapy.Request(url=url, callback=self.parseVersion_deep,
                                 meta={"version": response.meta["version"], "brand": response.meta["brand"],
                                       },
                                 )

        pass

    def parseQuote(self, response):
        # quote = response.body
        quote = response.xpath(".//pre/text()").extract_first()
        # print "=======quote======", quote, "\n"
        version = response.meta["version"]
        brand = response.meta["brand"]
        yield GsmarenaPhone(brand=brand, version=version, author=response.meta["author"],
                            location=response.meta["location"],
                            date=response.meta["date"], content=response.meta["content"],
                            quote_author=response.meta["quote_author"], quote_date=response.meta["quote_date"],
                            quote=quote)

        pass

    def errorback(self, response):
        print "===errorback==", response.code
        pass

    def parseDate(self, date):
        # str1 = "3 hrs 24 mins ago"
        # str1 = "17 days ago"
        # str1 = "7 hours ago"
        result_hours = re.search(r"(.*)hours?", date)
        result_minutes = re.search(r"(.*)minutes", date)
        if result_hours:
            hours = int(result_hours.groups()[0].strip())
            minutes = 0
        elif result_minutes:
            minutes = int(result_minutes.groups()[0].strip())
            hours = 0
        else:
            logger.error("==unKowntime")
            hours = 0
            minutes = 0
        hours = hours
        minutes = minutes
        now = datetime.now()
        delta = timedelta(hours=hours, minutes=minutes)
        n_days = now - delta
        n_days = n_days.strftime('%Y-%m-%d %H:%M:%S')
        print n_days
        return n_days
        pass
