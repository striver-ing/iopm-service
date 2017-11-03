# -*- coding: utf-8 -*-
'''
Created on 2017-09-22 15:55
---------
@summary:
---------
@author: Boris
'''
import sys
sys.path.append('..')

from utils.log import log
import utils.tools as tools
import web
import json
from service.format_keywords_service import format_keywords

class FormatKeywordsAction():
    def __init__(self):
        pass

    def deal_request(self):
        web.header('Content-Type','text/html;charset=UTF-8')

        data = json.loads(json.dumps(web.input()))
        print(data)

        keywords = data.get("keywords", '')
        keywords = format_keywords(keywords)

        return keywords

    def GET(self):
        return self.deal_request()

    def POST(self):
        return self.deal_request()

