# -*- coding: utf-8 -*-
import csv
import re

import os

import pymysql


class StockUtils:
    def getStockcodesFromDisk_list(self):
        '''从本地磁盘获取股票代码（list的形式）'''
        codes_list = []
        with open('stockcodes.txt', 'U') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                if re.search(r'\d', ''.join(row)):
                    codes_list.append(''.join(row))

        return codes_list

    def getStockcodesFromDisk_itera(self):
        '''从本地磁盘获取股票代码(生成器的形式)'''

        with open('stockcodes.txt', 'U') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                if re.search(r'\d', ''.join(row)):
                    yield ''.join(row)
        pass

    def insertToMysql_together(self):
        stockcodes = self.getStockcodesFromDisk_list()
        conn = pymysql.connect(host='127.0.0.1', port=3306, db='stockinfo',
                               user='root', passwd='')
        print len(stockcodes)
        for i in range(10):
            print stockcodes[i]

        cursor = conn.cursor()
        cursor.executemany("insert into stockcode(stockcode) VALUES (%s)", stockcodes)
        cursor.close()
        conn.commit()
        conn.close()
        pass

    def insertToMysql_onebyone(self):
        stockcodes = self.getStockcodesFromDisk_list()
        conn = pymysql.connect(host='127.0.0.1', port=3306, db='stockinfo',
                               user='root', passwd='')
        print len(stockcodes)
        for stockcode in stockcodes:
            cursor = conn.cursor()
            print stockcode
            cursor.execute("insert into stockcode(stockcode) VALUES (%s)", stockcode)
            cursor.close()

        conn.commit()
        conn.close()
        pass


if __name__ == '__main__':
    stockUtils = StockUtils()
    stockUtils.insertToMysql_onebyone()
    # stockUtils.insertToMysql_onebyone()
