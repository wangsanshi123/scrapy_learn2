# -*- coding: utf-8 -*-

import pymysql


def getDataSet(table, db='stockinfo', charset='utf8'):
    conn = pymysql.connect(host='127.0.0.1', port=3306, db=db,
                           user='root', passwd='', charset=charset)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {}".format(table))
    dataset = cursor.fetchall()
    cursor.close()
    conn.commit()
    return dataset


def connectsql(db='stockinfo'):
    conn = pymysql.connect(host='127.0.0.1', port=3306, db=db,
                           user='root', passwd='')
    cursor = conn.cursor()
    return cursor


def formatPrice():
    dataSet = getDataSet('gsmarena_phone_info')
    i = 0
    for data in dataSet:
        if i > 0:
            break
        print data
        i += 1
    pass


if __name__ == '__main__':
    formatPrice()
    pass
