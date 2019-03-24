# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
import datetime
from Jobbole.tools import get_number


def get_date(value):
    try:
        date = value.replace('·', '').strip()
        date_time = datetime.datetime.strptime(date, '%Y/%m/%d').date()
    except:
        date_time = datetime.datetime.now().date()
    return date_time


def get_value(value):
    return value


def get_tag(value):
    if '评论' in value:
        return ''
    else:
        return value


class JobboleInfoItem(ItemLoader):
    default_output_processor = TakeFirst()



class JobboleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    thumb_image_url = scrapy.Field()
    image_path = scrapy.Field()
    url = scrapy.Field()
    md5_url = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field(input_processor=MapCompose(get_date))
    tag = scrapy.Field(input_processor=MapCompose(get_tag),
                       output_processor=Join(','))
    comments = scrapy.Field(input_processor=MapCompose(get_number))
    content = scrapy.Field()
    collections = scrapy.Field(input_processor=MapCompose(get_number))
    praise = scrapy.Field(input_processor=MapCompose(get_number))





