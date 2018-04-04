# -*- coding: utf-8 -*-
import re
import time
import urlparse

import pymysql
import scrapy
from scrapy.utils.response import get_base_url

from scrapy_learn2.items import CforumTopicInfo, CforumReplyInfo


class CforumSpider(scrapy.Spider):
    name = "cforum"
    allowed_domains = ["cforum1.cari.com.my"]
    start_urls = ['https://cforum1.cari.com.my/forum.php?mod=forumdisplay&fid=1220']
    current_page_id = 0

    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, db='stockinfo',
                                    user='root', passwd='')
        cursor = self.conn.cursor()
        cursor.execute("SELECT max(last_update)FROM `cforum_topicinfo`")
        self.last_update_sql = str(cursor.fetchone()[0])
        cursor.close()
        self.conn.commit()

        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')

        pass

    def parse(self, response):

        print "==========last_update_sql=====================", self.last_update_sql

        #  //div[contains(@id,'in')]
        print "==========start parse====================="
        # urlparse.urljoin(get_base_url(response), next_page)
        baseurl = get_base_url(response)
        posts = response.xpath(".//tbody[contains(@id,'normalthread')]")

        for post in posts:
            belong = post.xpath(".//*[@id='listbox1']/em/a/text()").extract_first()
            topic = post.xpath(".//*[@id='listbox1']/a/text()").extract_first()
            author = post.xpath(".//*[@id='listbox2']/span[@class='thaut']/text()").extract_first()
            url = post.xpath(".//*[@id='listbox1']/a/@href").extract_first()
            post_date = post.xpath(".//*[@id='listbox2']/span[@class='thdate']/text()").extract_first()
            visite_num = post.xpath(".//*[@id='listbox2']/span[@class='thview']/text()").extract_first().split(":")[1]
            comment_num = post.xpath(".//*[@id='listbox2']/span[@class='thcmd']/text()").extract_first().split(":")[1]
            last_update = post.xpath(".//td[@class='by']/em/a/text()").extract_first()
            last_commentor = post.xpath(".//td[@class='by']/cite/a/text()").extract_first()

            url = urlparse.urljoin(baseurl, url)
            timeArray = time.strptime(post_date, "%d-%m-%Y")
            post_date = time.strftime("%Y-%m-%d", timeArray)

            timeArray = time.strptime(last_update, "%d-%m-%Y %H:%M %p")
            last_update = time.strftime("%Y-%m-%d %H:%M ", timeArray)

            # print "belong:", belong, "topic:", topic, "url:", url, "author:", author, " post_date:", post_date, "visite_num:", \
            #     visite_num, "\ncomment_num:", comment_num, "last_update:", last_update, "last_commentor", last_commentor, "\n   "

            item = CforumTopicInfo(belong=belong, topic=topic, url=url, author=author, post_date=post_date,
                                   visite_num=visite_num,
                                   comment_num=comment_num, last_update=last_update, last_commentor=last_commentor)
            if self.last_update_sql < last_update or self.last_update_sql == 'None':  # 根据时间做增量更新,精确到分钟
                yield item
        # next_page = "https://cforum1.cari.com.my/forum.php?mod=forumdisplay&fid=1220&page=2"
        next_page = response.xpath(".//*[@id='autopbn']/@rel").extract_first()
        next_page_id = re.search(r'.*?&page=(\d*$)', next_page).groups()[0]

        if next_page:
            if self.last_update_sql < last_update or self.last_update_sql == 'None':  # 根据时间做增量更新
                if self.current_page_id and int(self.current_page_id) > int(next_page_id):
                    pass
                else:
                    next_page_url = urlparse.urljoin(get_base_url(response), next_page)
                    print "===next_page_url====", next_page_url
                    yield scrapy.Request(url=next_page_url, callback=self.parse)
                    self.current_page_id = next_page_id
                print "=============current_page_id====================", self.current_page_id
            else:
                print "==============no content is update====================="

        else:
            print "================finish====================="

    def test(self, response):
        print "================test====================="

        pass
