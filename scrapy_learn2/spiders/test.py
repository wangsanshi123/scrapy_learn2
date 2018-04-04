# -*- coding: utf-8 -*-
import scrapy


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["forum1.cari.com.my"]
    start_urls = ['https://cforum1.cari.com.my/forum.php?mod=viewthread&tid=3957514&extra=page%3D1']
    def __init__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')

    def parse(self, response):
        print '========parse=============='
        divs = response.xpath(".//div[@id='postlist']/div[contains(@id,'post_')]")
        for div in divs:
            print "====len(divs)==========", len(divs)
            postnum = div.xpath(".//a[contains(@id,'postnum')]/em/text()").extract_first()
            print "======postnum==========", postnum

            author = div.xpath(".//div[@class='authi']/a/text()").extract_first()
            print "=====author======", author

            replytime = div.xpath(".//*[contains(@id,'authorposton')]/text()").extract_first()
            print "=====replytime======", replytime

            quote_temp = div.xpath(".//td[contains(@id,'postmessage')]/div[@class='quote']")
            quote_info = div.xpath(
                ".//td[contains(@id,'postmessage')]/div[@class='quote']//a/font/text()").extract_first()
            if quote_info:
                print "========quote_info==============", quote_info

                quote_author = quote_info.split("发表于")[0]
                quote_date = quote_info.split("发表于")[1]
                print "========quote_author==============", quote_author
                print "========quote_date==============", quote_date

                quote = quote_temp.xpath("string()").extract_first().strip(quote_info)
                print "========quote==============", quote
                content = div.xpath(".//td[contains(@id,'postmessage')]").xpath("string()").extract_first().strip(
                    quote_info + quote)
                print "======content==========", content
            else:
                content = div.xpath(".//td[contains(@id,'postmessage')]").xpath("string()").extract_first()
                print "======content==========", content

            print "\n\n"
            pass
