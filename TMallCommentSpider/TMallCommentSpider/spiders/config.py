# -*- coding: utf-8 -*-
# @Author : Huangcc

import urllib


search_keyword = '美年健康'


if __name__ == '__main__':
    print urllib.quote(search_keyword.decode('utf-8').encode('gbk'))
