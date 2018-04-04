# -*- coding: utf-8 -*-

import codecs
import json
import logging
from hashlib import md5
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from time import strftime, localtime

import MySQLdb
import MySQLdb.cursors
from scrapy import log
from twisted.enterprise import adbapi

from scrapy_learn2.items import StockinfoItem, CsdnblogcrawlspiderItem, CforumTopicInfo, CforumReplyInfo, Ips, \
    GsmarenaPhone, GsmarenaPhone_info

logger = logging.getLogger(__name__)


class CheckPipeline(object):
    def process_item(self, item, spider):
        for key in item:
            if item[key] is None:
                logger.info('%s is missing %s' % (item, key))
                # item[key] == 0
                item[key] == ""
        return item


class JsonWithEncodingCnblogsPipeline(object):
    def __init__(self):
        self.file = codecs.open('cnblogs.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MySQLStoreCnblogsPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.i = 0

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):

        if isinstance(item, StockinfoItem):
            d = self.dbpool.runInteraction(self._process_stockinfo, item, spider)
        elif isinstance(item, CsdnblogcrawlspiderItem):
            d = self.dbpool.runInteraction(self._process_cnblogsinfo, item, spider)
        elif isinstance(item, CforumTopicInfo):
            d = self.dbpool.runInteraction(self._process_cforumTopicinfo, item, spider)
        elif isinstance(item, CforumReplyInfo):
            d = self.dbpool.runInteraction(self._process_cforumReplyinfo, item, spider)


        elif isinstance(item, GsmarenaPhone):
            d = self.dbpool.runInteraction(self._process_gsmarenaPhone, item, spider)
        elif isinstance(item, GsmarenaPhone_info):
            d = self.dbpool.runInteraction(self._process_gsmarenaPhone_info, item, spider)


        elif isinstance(item, Ips):
            d = self.dbpool.runInteraction(self._process_Ips, item, spider)


        else:
            d = self.dbpool.runInteraction(self._process_nothing, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    # 将每行更新或写入数据库中
    def _process_stockinfo(self, conn, item, spider):
        try:
            conn.execute("insert into baseinfo1 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item['stockcode'], item['date'], item['open'], item['max'], item['close'], item['min'],
                          item['volume'], item
                          ['amount']))
            # print "========insert data==========", item['stockcode'], "   date:", item['date']
        except Exception, e:
            logger.error(e)
            pass

    def _process_cnblogsinfo(self, conn, item, spider):
        try:
            conn.execute("insert into cnblogs VALUES (%s,%s)", (item['blog_name'], item['blog_url']))
        except Exception, e:
            logger.error(e)
            pass

        pass

    def _process_cforumTopicinfo(self, conn, item, spider):

        now = strftime("%Y-%m-%d %H-%M-%S", localtime())

        conn.execute(" SELECT * FROM cforum_topicinfo  WHERE url =%s", (item['url'],))

        ret = conn.fetchone()

        try:
            if ret:

                conn.execute(
                    "update cforum_topicinfo set visite_num = %s,comment_num=%s,last_update =%s,last_commentor=%s, record_time = %s,new = %s where url = %s",
                    (item['visite_num'], item['comment_num'], item['last_update'], item['last_commentor'], now, 1,
                     item['url']))

                pass
            else:

                conn.execute("insert into cforum_topicinfo VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                             (item['belong'], item['topic'],
                              item['author'], item['url'],
                              item['post_date'],
                              item['visite_num'],
                              item['comment_num'],
                              item['last_update'],
                              item['last_commentor'], now, True))

            self.i += 1
            # print "=====new total item====", self.i
        except Exception, e:
            logger.error(e)

            pass

        pass

    def _process_cforumReplyinfo(self, conn, item, spider):
        ''' 处理回帖信息'''
        try:
            conn.execute("insert into cforum_replyinfo VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item['postnum'], item['author'], item['replytime'], item['quote_author'], item['quote_date'],
                          item['quote'],
                          item['content'], item['url']))
        except Exception, e:
            logger.error(e)
            pass

        pass

    def _process_nothing(self, conn, item, spider):
        # do nothing

        pass

    def _process_Ips(self, conn, item, spider):
        try:
            conn.execute("insert into ips VALUES (%s,%s,%s,%s)",
                         (item["ip"], item["port"], item["level"], item["check_count"]))
        except Exception, e:
            logger.error(e)
            pass
        pass

    def _process_gsmarenaPhone(self, conn, item, spider):
        try:
            conn.execute("insert into gsmarena_comments VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item["brand"], item["model"], item["author"], item["location"],
                          item["date"],
                          item["content"],
                          item["quote_author"],
                          item["quote_date"], item["quote"]))
        except Exception, e:
            logger.error(e)
            pass
        pass

    def _process_gsmarenaPhone_info(self, conn, item, spider):
        conn.execute(" SELECT * FROM gsmarena_phone_info  WHERE brand =%s and model=%s", (item['brand'], item['model']))

        ret = conn.fetchone()
        if ret:
            conn.execute(
                "update gsmarena_phone_info set network =%s,announced=%s, available = %s,dimensions = %s ,price= %s,comment_num = %s,url= %s where brand = %s and model=%s",
                (item['network'], item['announced'], item['available'], item['dimensions'],
                 item['price'], item['comment_num'], item['url'], item['brand'], item['model']))
            pass
        else:
            try:
                conn.execute("insert into gsmarena_phone_info VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                             (item["brand"], item['model'], item["network"], item["announced"], item["available"],
                              item["dimensions"],
                              item["price"],
                              item["comment_num"], item["url"], item['isContentUpdated']))
            except Exception, e:
                logger.error(e)
                pass
        pass

    # 获取url的md5编码
    def _get_linkmd5id(self, item):
        # url进行md5处理，为避免重复采集设计
        return md5(item['url'].encode('utf-8')).hexdigest()

    # 异常处理
    def _handle_error(self, failure, item, spider):
        log.err(failure)
