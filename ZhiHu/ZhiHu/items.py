# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy import Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Compose
from ZhiHu.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
import datetime
import re


def get_int_num(value):
    if re.match('.*?(\d+).*', value):
        num = int(re.match('.*?(\d+).*', value).group(1))
    else:
        num = 0
    return num


def change_num(value):
    if ',' in value:
        return ''.join(value.split(','))
    else:
        return value


class QuestionLoader(ItemLoader):
    default_output_processor = TakeFirst()


class AnswerLoader(ItemLoader):
    default_output_processor = TakeFirst()


class QuestionItem(scrapy.Item):
    zhihu_id = Field()
    topic = Field(output_processor=Join(','))
    url = Field()
    title = Field()
    content = Field()
    answer_num = Field(input_processor=MapCompose(change_num, get_int_num))
    comment_num = Field(input_processor=MapCompose(change_num, get_int_num))
    watcher_num = Field(input_processor=MapCompose(change_num, get_int_num))
    click_num = Field(input_processor=MapCompose(change_num, get_int_num))

    def insert_sql(self):
        sql = """
        insert into zhihu_question(zhihu_id,topic,url,title,
        content,answer_num,click_num,comment_num,watcher_num)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE content=VALUES(content),answer_num=VALUES(answer_num),
        click_num=VALUES(click_num),comment_num=VALUES(comment_num),
        watcher_num=VALUES(watcher_num)
        """
        params = (self['zhihu_id'],self['topic'],self['url'],self['title'],self['content'],self['answer_num'],self['click_num'],self['comment_num'],self['watcher_num'])
        return sql, params


class AnswerItem(scrapy.Item):
    zhihu_id = Field()
    url = Field()
    question_id = Field()
    answer_id = Field()
    content = Field()
    praise_num = Field()
    comment_num = Field()
    create_time = Field()
    update_time = Field()
    crawl_time = Field()

    def insert_sql(self):
        sql = """
        insert into zhihu_answer(zhihu_id, url, question_id, answer_id, content,
        praise_num,comment_num,create_time,update_time,crawl_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE content=VALUES(content),praise_num=VALUES(praise_num),comment_num=VALUES(comment_num)
        """
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        crawl_time = self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        params = (self['zhihu_id'],self['url'],self['question_id'],
                  self['answer_id'],self['content'],self['praise_num'],
                  self['comment_num'],create_time,update_time,
                  crawl_time)
        return sql, params