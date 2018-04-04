# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random

import time
from scrapy import signals
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from scrapy_learn2.utils.proxyutil import ProxyHelper

logger = logging.getLogger(__name__)


class ScrapyLearn2SpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        # logger.error("process_spider_input")
        print "=======process_spider_input======"

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        logger.error("process_spider_output")
        print "=======process_spider_output======"

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.
        logger.error("process_spider_exception")

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgent(object):
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))  # 返回的是本类的实例cls ==RandomUserAgent

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))


pass


class RandomProxy(object):
    def __init__(self, iplist):  # 初始化一下数据库连接
        # self.iplist = iplist
        self.iplist = ProxyHelper().getIpFromJson()

    @classmethod
    def from_crawler(cls, crawler):
        # 从Settings中加载IPLIST的值
        return cls(crawler.settings.getlist('IPLIST'))

    def process_request(self, request, spider):
        '''
        在请求上添加代理
        :param request:
        :param spider:
        :return:
        '''
        proxy = random.choice(self.iplist)
        request.meta['proxy'] = proxy


from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.webdriver.support import expected_conditions as EC


class PhantomJSMiddleware(object):
    def process_request(self, request, spider):
        if spider.name in ["gsmarena", "gsmarena_2", "gsmarenainfo", "gsmarenacomments"]:
            # print "PhantomJS is starting..."

            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0"
            )
            logger.info("===PhantomJS is starting...")
            driver = webdriver.PhantomJS()
            driver.get(request.url)
            # time.sleep(0.5)
            try:
                quote = request.meta["isQuote"]
            except:
                quote = None
                pass
            if not quote:
                "等待底部页面加载出来"
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//div[@class='footer-logo']")))
            else:
                time.sleep(1)
            body = driver.page_source
            # driver.close()

            return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
        else:
            print "====unKown_spider===="
            pass
