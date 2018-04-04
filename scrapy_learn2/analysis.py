# -*- coding: utf-8 -*-
import pymysql


class Analysis:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, db='stockinfo',

                                    user='root', passwd='')
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT max(date) FROM `baseinfo1` ")
        self.dataset = cursor.fetchone()[0]
        cursor.close()
        self.conn.commit()

        pass

    def getMaxFromDays(self, stockcode, day):
        ''' 指定股票的最新值相对于指定天数内的最大值下降百分比'''
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT max FROM `baseinfo1` WHERE `max` = (SELECT max(max) FROM `baseinfo1` where DATE_SUB(CURDATE(), INTERVAL (%s) DAY) <= date(date) AND `stockcode`=(%s)) AND stockcode = (%s) ",
            (day, stockcode, stockcode))
        dataset = cursor.fetchone()
        cursor.close()
        self.conn.commit()
        return dataset[0]

    def test2(self, date, stockcode):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT `close` FROM `baseinfo1` WHERE `date`= (%s) `stockcode`=(%s)", (date, stockcode))
        dataset = cursor.fetchone()
        cursor.close()
        self.conn.commit()
        return dataset[0]
        pass

    def test1(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT stockcode FROM `baseinfo1`")
        dataset = cursor.fetchall()
        cursor.close()
        self.conn.commit()
        for stockcode in dataset:
            stockcode = stockcode[0]

        pass

    pass


if __name__ == '__main__':
    analysis = Analysis()
    # print analysis.getMaxFromDays("600000", 30)
    # print analysis.test1()
    print analysis.test2("2016-09-02")
