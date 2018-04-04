# -*- coding: utf-8 -*-
import logging
import re
from datetime import datetime, timedelta
from time import strftime, strptime

import scrapy

from scrapy_learn2.items import GsmarenaPhone, GsmarenaPhone_info
from scrapy_learn2.utils import emailUtil
from scrapy_learn2.utils.dbbaseutil import MysqlUtil

logger = logging.getLogger(__name__)


class Gsmarena2Spider(scrapy.Spider):
    '''爬取每个手机品牌每个型号的评论量'''
    name = "gsmarena_2"
    allowed_domains = ["gsmarena.com"]
    # start_urls = ['http://www.gsmarena.com/vivo-phones-98.php', 'http://www.gsmarena.com/oppo-phones-82.php',
    #               'http://www.gsmarena.com/huawei-phones-58.php', 'http://www.gsmarena.com/xiaomi-phones-80.php',
    # 'http://www.gsmarena.com/zte-phones-62.php','http://www.gsmarena.com/samsung-phones-9.php']
    'https://www.gsmarena.com/vivo_v7-reviews-8937.php'
    start_urls = ['http://www.gsmarena.com/vivo-phones-98.php']
    base_url = "http://www.gsmarena.com/"
    brand = "samsung"
    quoteUrl_base = "http://www.gsmarena.com/comment.php3?idType=1&idComment="
    version = 'Mi Pad 2'

    # def start_requests(self):
    #     print "start_requests"
    #     url = "http://www.gsmarena.com/xiaomi_mi_pad_2-reviews-7770p2.php"
    #     yield scrapy.Request(url=url, callback=self.parseVersion_deep)

    def __init__(self):
        self.mysqlUtil = MysqlUtil()
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        pass

    def parse(self, response):
        "（根据指定品牌）分析品牌页面，得到各个型号的"
        items = response.xpath(".//div[@class='makers']//li")

        time = 0
        for item in items:
            # if time >= 30:
            #     logger.info(u"======爬取结束=======")
            #     break
            #     pass
            # if 24 <= time < 30:
            url = self.base_url + item.xpath(".//a/@href").extract_first()

            version = item.xpath(".//span/text()").extract_first()

            yield scrapy.Request(url=url, callback=self.parseVersion,
                                 meta={"version": version})
            # elif time > 32:
            #     logger.info(u"======爬取结束=======")
            #     break

            time += 1
        nextPage = response.xpath(".//*[@id='body']/div/div[3]/div[2]/a[2]/@href").extract_first()
        if nextPage:
            url = self.base_url + nextPage
            yield scrapy.Request(url=url, callback=self.parse)

    def parseVersion(self, response):
        "解析具体型号信息"
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
        price = price if price else 0

        commnent_num = response.xpath(".//*[@id='opinions-total']/b/text()").extract_first()

        yield GsmarenaPhone_info(brand=self.brand, version=response.meta["version"], network=network,
                                 announced=announced, available=available, dimensions=dimensions,
                                 price=price, commnent_num=commnent_num)

        url = response.xpath(".//a[@class='button']/@href").extract_first()
        try:
            url = self.base_url + url
            yield scrapy.Request(url=url, callback=self.parseVersion_deep,
                                 meta={"version": response.meta["version"]})
        except Exception, e:
            logger.error(e)
            pass

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
                print e
                pass

            pass
        return announced

    # 抓取指定型号手机的具体评论信息
    def parseVersion_deep(self, response):
        divs = response.xpath(".//div[@class='user-thread']")
        try:
            version = response.meta["version"]
        except:
            version = self.version
            pass
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

                    yield GsmarenaPhone(brand=self.brand, version=version, author=author, location=location, date=date,
                                        content=content,
                                        quote_author=quote_author, quote_date=quote_date, quote=quote)

                else:
                    quote_url = self.quoteUrl_base + quote_url.replace("#", "")
                    yield scrapy.Request(url=quote_url, callback=self.parseQuote,
                                         meta={"brand": self.brand, "version": version, "author": author,
                                               "location": location,
                                               "date": date, "content": content,
                                               "quote_author": quote_author, "quote_date": quote_date,
                                               "url": quote_url, "isQuote": True},
                                         )

            else:
                yield GsmarenaPhone(brand=self.brand, version=version, author=author, location=location, date=date,
                                    content=content,
                                    quote_author='', quote_date='', quote='')

        nextPage = response.xpath(".//a[@title='Next page']/@href").extract_first()
        #####################增量更新########################################

        if self.lastCommentDate and str(self.lastCommentDate) >= date:  # 用于增量更新
            print("=====increasing update====", date)
            return

        # 记录下最新评论的时间
        if time == 1:
            self.mysqlUtil.cur.execute("update gsmarena_phone_info set lastCommentDate=%s where brand=%s,version=%s",
                                       (date, self.brand, self.version))
            self.mysqlUtil.conn.commit()
        ######################增量更新###################################

        if nextPage:
            url = self.base_url + nextPage

            yield scrapy.Request(url=url, callback=self.parseVersion_deep,
                                 meta={"version": version,
                                       },
                                 )

        pass

    def parseQuote(self, response):

        quote = response.xpath(".//pre/text()").extract_first()

        version = response.meta["version"]
        brand = response.meta["brand"]
        yield GsmarenaPhone(brand=brand, version=version, author=response.meta["author"],
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

    def close(self, reason):  # 爬取结束的时候发送邮件
        print "===close==="
        with open("exceptions.txt", 'r') as f:
            message = f.read().decode('utf-8')
            emailUtil.sendMsg_QQ(info=(u'具体信息：' + message))
