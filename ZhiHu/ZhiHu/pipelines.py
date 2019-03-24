# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors


class ZhihuPipeline(object):
    def process_item(self, item, spider):
        return item


class TwistedMysqlPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_crawler(cls, crawler):
        params = dict(
            host = crawler.settings.get('HOST'),
            user = crawler.settings.get('USER'),
            passwd = crawler.settings.get('PASSWORD'),
            db = crawler.settings.get('DB_NAME'),
            charset = 'utf8',
            use_unicode = True,
            cursorclass = MySQLdb.cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **params)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.insert, item)
        query.addErrback(self.print_failure, item, spider)

    def print_failure(self, failure, item, spider):
        print(failure)

    def insert(self, cursor, item):
        sql, params = item.insert_sql()
        cursor.execute(sql, params)
