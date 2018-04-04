# -*- coding: utf-8 -*-
import logging
import re
from time import strftime, strptime

import scrapy
from datetime import datetime, timedelta

from scrapy_learn2.items import GsmarenaPhone
from scrapy_learn2.utils.dbbaseutil import MysqlUtil

logger = logging.getLogger(__name__)


class GsmarenacommentsSpider(scrapy.Spider):
    " # 抓取指定型号手机的具体评论信息"
    name = "gsmarenacomments"

    def __init__(self):
        self.mysqlUtil = MysqlUtil()
        self.base_url = "http://www.gsmarena.com/"
        self.quoteUrl_base = "http://www.gsmarena.com/comment.php3?idType=1&idComment="

        pass

    def start_requests(self):
        dataSet = self.mysqlUtil.select('gsmarena_phone_info')
        for item in dataSet:
            brand = item['brand']
            model = item['model']
            url = item['url']
            isContentUpdated = item["isContentUpdated"]
            if not isContentUpdated:  # 只有没用更新过的内容才会被爬取
                yield scrapy.Request(url=self.base_url + url,
                                     meta={"brand": brand, "model": model})
            pass
        pass

    def parse(self, response):
        divs = response.xpath(".//div[@class='user-thread']")
        brand = response.meta["brand"]
        model = response.meta["model"]


        time = 0
        for div in divs:
            time += 1
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
                # logger.info(e)
                date = self.parseDate(date)
                pass

            quote_temp = div.xpath(".//p[@class='uopin']/span")
            quote_partial = quote_temp.xpath("string()").extract_first()
            # quote_date = div.xpath(".//a[@class='uinreply']/text()").extract_first()
            quote_date = div.xpath(".//*[@class='uinreply']/text()").extract_first()

            content = div.xpath(".//p[@class='uopin']")
            content = content.xpath("string()").extract_first()

            if quote_temp:
                quote_data_temp = quote_date.split(",") if "," in quote_date else quote_date.split(" ")
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
                    # logger.info(e)
                    quote_date = self.parseDate(quote_date)

                    pass
                quote_url = div.xpath(".//span[@class='uinreply-msg']/a/@href").extract_first()
                if not quote_url:
                    quote = div.xpath(".//span[@class='uinreply-msg uinreply-msg-single']/text()").extract_first()

                    yield GsmarenaPhone(brand=brand, model=model, author=author, location=location,
                                        date=date,
                                        content=content,
                                        quote_author=quote_author, quote_date=quote_date, quote=quote)

                else:
                    quote_url = self.quoteUrl_base + quote_url.replace("#", "")
                    yield scrapy.Request(url=quote_url, callback=self.parseQuote,
                                         meta={"brand": brand, "model": model, "author": author,
                                               "location": location,
                                               "date": date, "content": content,
                                               "quote_author": quote_author, "quote_date": quote_date,
                                               "url": quote_url, "isQuote": True},
                                         )

            else:
                yield GsmarenaPhone(brand=brand, model=model, author=author, location=location, date=date,
                                    content=content,
                                    quote_author='', quote_date='', quote='')

                #####################增量更新########################################
                ### 更新概要表的isContentUpdated字段，表示评论内容已经被爬取了
                self.mysqlUtil.cur.execute("update gsmarena_phone_info set isContentUpdated=%s where brand=%s",
                                           (1, brand))

                ######################增量更新###################################
        pass
        nextPage = response.xpath(".//a[@title='Next page']/@href").extract_first()

        if nextPage:
            url = self.base_url + nextPage

            yield scrapy.Request(url=url,
                                 meta={"brand": brand, "model": model},
                                 )
        pass

    def parseQuote(self, response):

        quote = response.xpath(".//pre/text()").extract_first()

        model = response.meta["model"]
        brand = response.meta["brand"]
        yield GsmarenaPhone(brand=brand, model=model, author=response.meta["author"],
                            location=response.meta["location"],
                            date=response.meta["date"], content=response.meta["content"],
                            quote_author=response.meta["quote_author"], quote_date=response.meta["quote_date"],
                            quote=quote)

        pass

    def parseDate(self, date):
        result_hours = re.search(r"(.*)hours?", date)
        result_minutes = re.search(r"(.*)minutes", date)
        if result_hours:
            hours = int(result_hours.groups()[0].strip())
            minutes = 0
        elif result_minutes:
            minutes = int(result_minutes.groups()[0].strip())
            hours = 0
        else:
            logger.error(u"未知时间格式，该帖子可能被删除", )
            hours = 0
            minutes = 0
        hours = hours
        minutes = minutes
        now = datetime.now()
        delta = timedelta(hours=hours, minutes=minutes)
        n_days = now - delta
        n_days = n_days.strftime('%Y-%m-%d %H:%M:%S')
        return n_days
        pass
