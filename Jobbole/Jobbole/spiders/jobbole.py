# -*- coding: utf-8 -*-
import scrapy
from Jobbole.items import JobboleItem, JobboleInfoItem
from scrapy.http import Request
from urllib.parse import urljoin
from Jobbole.tools import get_md5
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):

    name = 'jobbole'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    # def __init__(self):
    #     super(JobboleSpider).__init__()
    #     self.browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def spider_closed(self, spider):
    #     print('spider closed')
    #     self.browser.quit()


    def parse(self, response):
        for info in response.css('#archive div.post.floated-thumb'):
            article_url = info.css('div.post-thumb a::attr(href)').extract()[0]
            thumb_image_url = info.css('div.post-thumb a img::attr(src)').extract()
            yield Request(url=urljoin(response.url, article_url), callback=self.parse_detail, meta={'thumb_image_url': thumb_image_url})
        next_page = response.css('.next.page-numbers::attr(href)').extract()[0]
        yield Request(url=urljoin(response.url, next_page), callback=self.parse)

    def parse_detail(self, response):
        url = response.url
        md5_url = get_md5(url)
        item_loader = JobboleInfoItem(item=JobboleItem(), response=response)
        item_loader.add_value('thumb_image_url', [response.meta.get('thumb_image_url', '')])
        item_loader.add_value('url', url)
        item_loader.add_value('md5_url', md5_url)
        item_loader.add_css('title','.entry-header h1::text')
        item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_css('tag', '.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('content', 'div.entry' )
        item_loader.add_css('comments', 'a[href="#article-comment"] span::text' )
        item_loader.add_css('collections', '.post-adds span:nth-child(2)::text')
        item_loader.add_css('praise', '.post-adds span:nth-child(1) h10::text')
        article_item = item_loader.load_item()

        yield article_item


