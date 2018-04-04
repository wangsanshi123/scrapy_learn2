import scrapy


class TestSpider_faflj(scrapy.Spider):
    name = 'test2'
    start_urls = ['http://www.baidu.com']
    url = "http://blog.csdn.net/team77/article/details/50827505"

    def parse(self, response):
        print "=======parse========="
        test1 = self.test1()
        # next(test1)
        yield next(test1)
        pass

    def test1(self):
        print "=======test1========="
        yield scrapy.Request(url=self.url, callback=self.test2)

    def test2(self, response):
        print "=======test2========="
