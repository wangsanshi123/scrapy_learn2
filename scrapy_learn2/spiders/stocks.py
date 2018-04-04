# -*- coding: utf-8 -*-
import re
import time

import pymysql
import scrapy
from scrapy import Spider

from scrapy_learn2.items import StockinfoItem


class StocksSpider(Spider):
    name = 'stocks'
    allowed_domains = ['money.finance.sina.com.cn']

    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, db='stockinfo',
                                    user='root', passwd='')

        cur = self.conn.cursor()
        cur.execute('SELECT * FROM `baseinfo1` WHERE date = (SELECT max(date) FROM `baseinfo1`)')

        record = cur.fetchone()
        if record:
            self.last_year = record[1].year
            self.last_month = record[1].month
        else:
            self.last_year = 2010
            self.last_month = 4
        pass

    # start_urls = [
    #     'http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/600939.phtml?year=2017&jidu=2', ]

    def start_requests(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT stockcode FROM `stockcode`")
        stockcodes = cursor.fetchall()
        cursor.close()
        self.conn.commit()

        i = 0
        for stockcode in stockcodes:
            # if i <= 4:
            #     pass
            if i < 3:
                times = self.getYearAndJidu()
                for time in times:
                    year = time[0]
                    jidu = time[1]
                    url = 'http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{}.phtml?year={}&jidu={}'.format(
                        stockcode[0], year, jidu)
                    yield scrapy.Request(url=url, meta={'stockcode': stockcode[0]})
                print "=========now is crawl:=========", stockcode
                print "=========now is time:=========", i
            else:
                print "=========over========="
                break
            i += 1
            pass

    def parse(self, response):

        tds = response.xpath(".//*[@id='FundHoldSharesTable']//tr/td")

        # print "===========len(tds)============", len(tds)

        pattern = re.compile(r"\d.*?\d$")
        temps_list = []  # 存放解析好的股票信息
        for i in range(len(tds)):
            # temp = tds[i].xpath("string()").extract()[0].replace(u'\xa0', u' ').strip()
            temp = tds[i].xpath("string()").extract()[0].strip()
            if pattern.match(temp):
                # print "=================", temp
                temps_list.append(temp)
            else:
                # print "======temp is null===========", temp
                pass
        # print len(temps_list)
        position = 0
        for i in temps_list:

            if position + 7 < len(temps_list):
                item = StockinfoItem()  # 实例item（具体定义的item类）,将要保存的值放到事先声明的item属性中
                item['stockcode'] = response.meta['stockcode']
                item['date'] = temps_list[position + 0]
                item['open'] = temps_list[position + 1]
                item['max'] = temps_list[position + 2]
                item['close'] = temps_list[position + 3]
                item['min'] = temps_list[position + 4]
                item['volume'] = temps_list[position + 5]
                item['amount'] = temps_list[position + 6]
                yield item  # 返回item,这时会自动解析item
            position += 7



            # todo 新的请求

    def getStockInfo(self, stockcode):
        '''根据股票代码，获得相关股票信息并将之存到数据库'''
        pass

    def getYearAndJidu(self):

        # 该方法会根具当前时间和上次更新时间确定出应该更新的年份和季度,返回一个年份和季度的列表

        list_time = []
        year_current = int(time.strftime('%Y-%m', time.localtime(time.time())).split('-')[0])

        jidu_current = int(time.strftime('%Y-%m', time.localtime(time.time())).split('-')[1]) / 3 + 1
        month_current = int(time.strftime('%Y-%m', time.localtime(time.time())).split('-')[1])

        if month_current >= self.last_month:
            jidu = (month_current - self.last_month) / 3 + 2 + (year_current - self.last_year) * 4
        else:
            jidu = (month_current + 12 - self.last_month) / 3 + (year_current - 1 - self.last_year) * 4
        pass

        for i in range(jidu):
            list_time.append((year_current, jidu_current))
            if jidu_current - 1 > 0:
                jidu_current = jidu_current - 1
            else:
                jidu_current = jidu_current + 4 - 1
                year_current = year_current - 1

        return list_time
