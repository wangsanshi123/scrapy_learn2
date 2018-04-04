# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scrapy_learn2.items import CsdnblogcrawlspiderItem


class CnblogsSpider(CrawlSpider):
    name = 'cnblogs'
    allowed_domains = ['blog.csdn.net']
    start_urls = ['http://blog.csdn.net/u012150179/article/details/11749017', ]

    # rules = (
    #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    # )

    rules = [
        Rule(LinkExtractor(allow=('/u012150179/article/details'),
                           restrict_xpaths=('//li[@class="next_article"]')),
             callback='parse_item',
             follow=True)
    ]

    def parse_item(self, response):
        # i = {}
        # # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        # # i['name'] = response.xpath('//div[@id="name"]').extract()
        # # i['description'] = response.xpath('//div[@id="description"]').extract()
        # return i

        print "parse_item>>>>>>"
        item = CsdnblogcrawlspiderItem()
        sel = Selector(response)
        blog_url = str(response.url)
        blog_name = sel.xpath('//div[@id="article_details"]/div/h1/span/a/text()').extract()
        # item['blog_name'] = [n.encode('utf-8') for n in blog_name]
        if blog_name:
            item['blog_name'] = blog_name[0]

        item['blog_url'] = blog_url.encode('utf-8')

        yield item
