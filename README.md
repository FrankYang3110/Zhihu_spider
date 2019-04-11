# Zhihu_spider
Practice project

Scrapy抓取知乎全部问题和答案，存入mysql数据库。

开始用selenium模拟登陆知乎，然后将cookies保存，交给后面的Request

用twisted提供的异步接口将数据存入mysql

