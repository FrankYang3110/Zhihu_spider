# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import MySQLdb
from twisted.enterprise import adbapi
from MySQLdb.cursors import DictCursor


class JobbolePipeline(object):
    def process_item(self, item, spider):
        return item


class ImagePathPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, i in results:
            path = i.get('path')
            item['image_path'] = path
        return item


class MysqlPipeline(object):
    def __init__(self, host, user, passwd, db):
        self.conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8', use_unicode=True)

    @classmethod
    def from_crawler(cls, crawler):
        host = crawler.settings.get('HOST')
        user = crawler.settings.get('USER')
        passwd = crawler.settings.get('PASSWROD')
        db = crawler.settings.get('DBNAME')
        return cls(host, user, passwd, db)

    def process_item(self, item, spider):
        cursor = self.conn.cursor()
        insert_sql = """
        insert into jobbole(thumb_image_url, url,md5_url,title,create_date,tag,comments,content,collections,praise)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(insert_sql, (item['thumb_image_url'],item['url'],item['md5_url'],item['title'],item['create_date'],item['tag'],item['comments'],item['content'],item['collections'],item['praise']))
        self.conn.commit()


class TwistedMysqlPipeline(object):
    def __init__(self, host, user, passwd, db):
        param = dict(host=host,
                     user=user,
                     passwd=passwd,
                     db=db,
                     charset='utf8',
                     use_unicode=True,
                     cursorclass=DictCursor
                     )
        self.dbpool = adbapi.ConnectionPool('MySQLdb', **param)

    @classmethod
    def from_crawler(cls, crawler):
        host = crawler.settings.get('HOST')
        user = crawler.settings.get('USER')
        passwd = crawler.settings.get('PASSWROD')
        db = crawler.settings.get('DBNAME')
        return cls(host, user, passwd, db)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
               insert into jobbole(thumb_image_url, url,md5_url,title,
               create_date,tag,comments,content,collections,praise)
               values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update
               comments=values(comments),content=values(content),content=values(content),
               collections=values(collections),praise=values(praise),
               """
        cursor.execute(insert_sql, (item['thumb_image_url'],item['url'],item['md5_url'],item['title'],item['create_date'],item['tag'],item['comments'],item['content'],item['collections'],item['praise']))




