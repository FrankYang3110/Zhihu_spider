#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import sys
import os
from scrapy import cmdline

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
cmdline.execute(['scrapy', 'crawl', 'zhihu'])
