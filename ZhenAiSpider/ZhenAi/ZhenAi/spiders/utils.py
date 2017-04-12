# -*- coding: utf-8 -*-

import re


def get_brief_td_to_key_value(td):
    p = '<span.*?>(.*?)[：:]?\s?</span>(.*?)</td>'
    result = re.findall(p, td)
    if len(result) == 1:
        return result[0][0].replace(u'\uff1a', ''), result[0][1]
    else:
        return None, None


def get_info_td_to_key_value(td):
    p = '<span.*?>(.*?)[：:]?\s?</span>'
    result = re.findall(p, td)
    if len(result) == 2:
        return result[0].replace(u'\uff1a', ''), result[1]
    else:
        return None, None
