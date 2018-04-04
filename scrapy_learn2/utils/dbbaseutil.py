# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
from pymysql import cursors

default_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root', 'password': '',
    'charset': 'utf8',
    'cursorclass': cursors.DictCursor,
    'db': 'stockinfo'
}

online_config = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'ue_all',
    'password': 'FKbnqxEw7htu}DBSk',
    'cursorclass': cursors.DictCursor
}

test_config = {
    'host': '192.168.2.97',
    'port': 3302,
    'user': 'testue',
    'password': 'testue',
    'cursorclass': cursors.DictCursor
}


class MysqlUtil():
    '''
    实现数据库代理者中定义的抽象接口
    底层是mysql数据库时的操作代理类
    '''

    def __init__(self, config=None):
        '''
        实现数据库的基本配置
        登录远程数据库、配置编码
        '''
        if not config:
            config = default_config
        config['charset'] = 'utf8'
        self.conn = pymysql.connect(**config)
        self.cur = self.conn.cursor()
        self.cur.execute("set character_set_database = 'utf8'")
        self.cur.execute("set character_set_server = 'utf8'")
        self.conn.commit()
        self.conflict = dict()
        self.conflict['ignore'] = 'insert ignore into'
        self.conflict['replace'] = 'replace into'

    def create_database(self, database):
        '''
        创建数据库
        '''
        self.cur.execute('create database %s' % database)
        print('create database successful')

    def connect(self, database):
        '''
        连接到相应的数据库
        '''
        self.cur.execute('use %s' % database)
        print('connect database successful')

    def create_table(self, table, field_dict, primary_key):
        '''
        创建数据表
        :param table: 表名
        :param field_dict: 字段名称以及字段类型 例如 {'content':'text', 'buy_time':'datetime'}
        :param primary_key: 指明数据表的主键 例如 ['item_id', 'sellerid']
        '''
        create_sql_formate = 'create table %s (%s primary key (%s)) default character set utf8'
        field_str = ''
        for field in field_dict:
            field_str += '%s %s, ' % (field, field_dict[field])
        create_sql_str = create_sql_formate % (table, field_str, ', '.join(primary_key))
        self.cur.execute(create_sql_str)

    def select(self, table, field_list=None, condition=None, sql_suffix=''):
        '''
        从数据库中获取数据，并以列表形式返回
        :param table: 数据所在的表名
        :param field_list: 要获取的字段列表
        :param condition: 数据的筛选条件，格式为 {'model = ': 'mate9'} 即字段 model 的值为 mate9 的所有记录
        :param sql_suffix: 其他的一些附加条件，比如说 order by desc group by limit 等等，可以拼接在最后，实现更灵活的查询
        '''
        fields_string = '*'
        if field_list:
            fields_string = ', '.join(field_list)
        select_sql = 'select %s from %s' % (fields_string, table)
        if condition:
            condition_string = ' and '.join([key + '%s' for key in condition.keys()])
            select_sql += ' where %s' % condition_string
            select_sql += sql_suffix
            self.cur.execute(select_sql, tuple(condition.values()))
        else:
            select_sql += sql_suffix
            self.cur.execute(select_sql)
        return self.cur.fetchall()

    def insert(self, table, records, field_list=None, conflict='ignore'):
        '''
        将数据插入数据表，遇到重复数据忽略
        :param table: 数据表名称
        :param records: 待插入的数据列表，格式为[{'content': '手机不错', 'date': '2016-1-1'}, {'content': '卡顿', 'date': '2016-3-8'}]
        :param field_list: 如果传入值，则只取 field_list 当中的字段 比如 ['content'] 只取记录中的 content字段
        :param conflict: 当遇到记录的主键冲突时，该字段设置处理的方法 'ignore': 简单的忽略尚未插入的冲突数据 'replace': 用当前冲突的待插入数据替换数据库中冲突数据
        '''
        new_records = records
        if field_list:
            new_records = list()
            for record in records:
                new_record = dict()
                new_record = {field: record[field] for field in field_list}
                new_records.append(record)

        for record in new_records:
            insert_sql = '%s %s (%s) values (%s)' % (
                self.conflict[conflict], table, ', '.join(record.keys()), ', '.join(['%s'] * len(record.keys())))
            self.cur.execute(insert_sql, tuple(record.values()))
            self.conn.commit()

    def update(self, table, field_list, condition, record):
        '''
        更新记录的某些字段
        :param table: 数据表
        :param field_list: 要更新的字段列表
        :param condition: 要更新的记录需要满足的条件
        :param record: 待更新的记录
        '''
        value_list = list()
        for key in field_list + condition:
            value_list.append(record[key])
        field = [item + ' = %s' for item in field_list]
        set_part = ', '.join(field)
        condition = [item + ' = %s' for item in condition]
        where_part = ' and '.join(condition)
        update_sql = 'UPDATE %s SET %s WHERE %s' % (table, set_part, where_part)
        self.cur.execute(update_sql, value_list)
        self.conn.commit()

        # def update_new(self, table, field, condition, record):
        #     '''
        #          更新记录的某些字段
        #          :param table: 数据表
        #          :param field_list: 要更新的字段列表
        #          :param condition: 要更新的记录需要满足的条件
        #          :param record: 待更新的记录
        #     '''
        #     #    conn.execute("update cforum_topicinfo set where url = %s", ())
        #
        #     condition_string = ' and '.join([key + '%s' for key in condition.keys()])
        #
        #     self.cur.execute(select_sql, tuple(condition.values()))
        #
        # # condition = [item + ' = %s' for item in condition]
        # where_part = ' and '.join(condition)
        # update_sql = 'UPDATE %s SET %s=%s WHERE %s' % (table, field, record, where_part)
        # self.cur.execute(update_sql)
        # self.conn.commit()
        # pass

    def remove_repeat(self, table, drop_field_list, format_func):
        '''
        可以说这是因为最初数据库设计不够良好导致的
        因为更新的时候总是会重复插入某些数据
        现有的主键无法做到去重，并且将文本加入主键不够方便
        该函数则希望弥补这一缺陷，不过数据量、效率方面有待考证
        :param table: 数据表名称
        :param drop_field_list: 去除重复的依据字段列表
        :param format_func: 去重之后的数据进行格式化的函数
        '''
        sql = 'select * from %s' % table
        df = pd.read_sql(sql, self.conn)
        print(df.shape)
        for field in drop_field_list:
            df.drop(field, axis=1, inplace=True)
        df.drop_duplicates(inplace=True)
        print(df.shape)
        content = df.to_dict(orient='records')
        for item in content:
            format_func(item)
        self.cur.execute('truncate table %s' % table)
        self.insert(table, content)

    def delete(self, table, condition_list):
        '''
        根据条件删除记录
        :param table: 待删除数据所在表格
        :param condition_list: 待删除数据需要满足的条件列表
        '''
        for condition in condition_list:
            where_part = ' and '.join([item + ' = %s' for item in list(condition.keys())])
            sql = 'delete from %s where %s' % (table, where_part)
            self.cur.execute(sql, list(condition.values()))
            self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
        print('mysql closed')


if __name__ == '__main__':
    mysql = MysqlUtil()
    # dataSet1 = mysql.select('ips', condition={'ip=': '92.63.238.211'})
    # print len(dataSet1)
    #
    # dataSet2 = mysql.select('stockcode', condition={'stockcode=': '600011'})
    # print len(dataSet2)

    # mysql.update('ips', ['port'], ['ip= 92.63.238.211'], 0)
    # conn.execute("update cforum_topicinfo set port =%s,where url = %s", ())
    table = 'ips'
    column = 'ip'
    ip = '92.63.238.211'
    port = 3
    # mysql.conn.execute("update % set where % = %s", (table, column, ip))
    # mysql.cur.execute("update ips set port =%s where ip = %s", (port, ip))

    # mysql.cur.execute("insert into user VALUES (%s,%s,%s)", (2, 'y', "2"))
    # mysql.cur.execute("select 1 from toutiao_article where group_id=%s", (123))
    # mysql.cur.execute("select * from ips where port=%s", (port))
    # ret = mysql.cur.fetchone()
    # print ret
    dataSet2 = mysql.select('ips',condition={'ip=':'92.63.238.211'})
    # dataSet2 = mysql.select('toutiao_comment')
    print(dataSet2)
    mysql.conn.commit()
    mysql.close()
