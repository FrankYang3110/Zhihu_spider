# -*- coding: utf-8 -*-
import time
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from items import AnswerItem, AnswerLoader, QuestionItem, QuestionLoader
import re
from urllib.parse import  urljoin
import random
import json
import datetime


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']

    def __init__(self):
        super(ZhihuSpider).__init__()
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36',
        ]
        ua = random.choice(ua_list)
        self.headers = {'User-Agent': ua}

    def start_requests(self):
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
        browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', options=chrome_options)
        browser.get('https://www.zhihu.com/signup?next=%2F')
        time.sleep(3)
        browser.find_element_by_css_selector('.SignContainer-switch span').click()
        time.sleep(1)
        browser.find_element_by_css_selector('input[name=username]').send_keys(18570048055)
        time.sleep(1)
        browser.find_element_by_css_selector('input[name=password]').send_keys(2487120)
        time.sleep(1)
        browser.find_element_by_css_selector('button[type=submit]').click()
        time.sleep(10)
        cookies_dict = {}
        # ua = UserAgent()
        # 因为知乎对浏览器版本的要求比较高，fake-useragent里面的浏览器很多版本过低，所以选择自己构建一些useragent列表
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        for cookie in browser.get_cookies():
            cookies_dict[cookie['name']] = cookie['value']
        browser.close()
        yield scrapy.Request(url=self.start_urls[0], headers=self.headers, dont_filter=True, cookies=cookies_dict)

    def parse(self, response):
        '''
        深度优先：提取页面中所有的url，如果url符合/question/***则下载之后直接即进入解析函数
        '''
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith('https') else False,all_urls)
        for url in all_urls:
            match_url = re.match(r"(.*www.zhihu.com/question/(\d+))(/|$).*", url)
            if match_url:
                request_url = match_url.group(1)
                question_id = match_url.group(2)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
                break

            else:
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        match_url = re.match(r"(.*www.zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_url:
            question_id = int(match_url.group(2))
            anser_url = 'https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={}&offset={}'

            question_item_loader = QuestionLoader(item=QuestionItem(), response=response)
            question_item_loader.add_css('title', 'h1.QuestionHeader-title::text')
            question_item_loader.add_css('content', 'div.QuestionHeader-detail')
            question_item_loader.add_value('url', response.url)
            question_item_loader.add_value('zhihu_id', question_id)
            question_item_loader.add_css('answer_num', '.List-headerText span::text')
            question_item_loader.add_css('comment_num', '.QuestionHeader-Comment button::text')
            question_item_loader.add_css('watcher_num', '.QuestionFollowStatus strong.NumberBoard-itemValue::text')
            question_item_loader.add_css('click_num', '.NumberBoard.QuestionFollowStatus-counts.NumberBoard--divider div:nth-child(2) .NumberBoard-itemInner .NumberBoard-itemValue::text')
            question_item_loader.add_css('topic', '.QuestionHeader-topics div.Popover div::text')

            quesion_item = question_item_loader.load_item()
            yield scrapy.Request(url=anser_url.format(question_id, 5, 0), headers=self.headers, callback=self.parse_answer)
            yield quesion_item

    def parse_answer(self, response):
        answer_item = AnswerItem()
        answer_json = json.loads(response.text)
        is_end = answer_json['paging']['is_end']
        next_page = answer_json['paging']['next']

        for answer in answer_json['data']:
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['answer_id'] = answer['author']['id'] if 'author' in answer else None
            answer_item['content'] = answer['content'] if 'content'in answer else None
            answer_item['praise_num'] = answer['voteup_count']
            answer_item['comment_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()

            yield answer_item
        if not is_end:
            yield scrapy.Request(url=next_page, headers=self.headers, callback=self.parse_answer)









