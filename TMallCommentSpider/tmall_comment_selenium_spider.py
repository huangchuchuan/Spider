# -*- coding: utf-8 -*-
# @Author : Huangcc

from selenium import webdriver

browser = webdriver.Firefox()
browser.get('https://list.tmall.com/search_product.htm?q=%C3%C0%C4%EA%BD%A1%BF%B5&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton')
html_source = browser.page_source
print html_source
browser.close()