#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import hashlib
import re

def get_md5(url):
    hash = hashlib.md5()
    if isinstance(url, str):
        hash.update(url.encode('utf-8'))
        return hash.hexdigest()
    else:
        hash.update(url)
        return hash.hexdigest()


def get_number(str_object):
    p = re.match(r'.*(\d+).*', str_object)
    if p:
        number = int(p.group(1)) # 因为在数据库中设置的数字字段为整形，所以需要用int()
    else:
        number = 0
    return number



