# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class StockinfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stockcode = scrapy.Field()
    date = scrapy.Field()
    open = scrapy.Field()
    max = scrapy.Field()
    close = scrapy.Field()
    min = scrapy.Field()
    volume = scrapy.Field()
    amount = scrapy.Field()

    pass


class CsdnblogcrawlspiderItem(scrapy.Item):
    blog_name = scrapy.Field()
    blog_url = scrapy.Field()
    pass


class CforumTopicInfo(scrapy.Item):
    belong = scrapy.Field()
    topic = scrapy.Field()
    author = scrapy.Field()
    url = scrapy.Field()
    post_date = scrapy.Field()
    visite_num = scrapy.Field()
    comment_num = scrapy.Field()
    last_update = scrapy.Field()
    last_commentor = scrapy.Field()
    pass


class CforumReplyInfo(scrapy.Item):
    postnum = scrapy.Field()
    author = scrapy.Field()
    replytime = scrapy.Field()
    quote_author = scrapy.Field()
    quote_date = scrapy.Field()
    quote = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()

    pass


class Ips(scrapy.Item):
    ip = scrapy.Field()
    port = scrapy.Field()
    level = scrapy.Field()
    check_count = scrapy.Field()


class GsmarenaPhone(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()

    author = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field()  # 发表时间
    content = scrapy.Field()

    quote_author = scrapy.Field()
    quote_date = scrapy.Field()  # 引用时间
    quote = scrapy.Field()


class GsmarenaPhone_info(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()
    network = scrapy.Field()
    announced = scrapy.Field()
    available = scrapy.Field()
    dimensions = scrapy.Field()
    price = scrapy.Field()
    comment_num = scrapy.Field()
    url = scrapy.Field()
    isContentUpdated = scrapy.Field()
