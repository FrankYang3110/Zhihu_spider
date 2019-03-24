#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from scrapy import cmdline
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
cmdline.execute(['scrapy', 'crawl', 'jobbole'])


