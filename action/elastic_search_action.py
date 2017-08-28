# -*- coding: utf-8 -*-
'''
Created on 2017-08-02 09:24
---------
@summary: 热点相关性排序
---------
@author: Boris
'''
import web
from service.elastic_search_server import ElasticSearchServer
from utils.log import log
import json

class ElasticSearchAction(object):
    def __init__(self):
        self._elastic_search_server = ElasticSearchServer()

    def GET(self):
        web.header('Content-Type','text/html;charset=UTF-8')
        print(str(web.input()))
        data = json.loads(json.dumps(web.input()))

        table = data.get('table')
        body = data.get('body')

        if not table or not body:
            return 'table 和 body 不能为空'

        result = {}

        try:
            result = self._elastic_search_server.search(table, body)
        except Exception as e:
            log.error(e)

        return result

    def POST(self):
        web.header('Content-Type','text/html;charset=UTF-8')
        print(str(web.input()))
        data = json.loads(json.dumps(web.input()))

        table = data.get('table')
        body = data.get('body')

        if not table or not body:
            return 'table 和 body 不能为空'

        result = {}

        try:
            result = self._elastic_search_server.search(table, body)
        except Exception as e:
            log.error(e)

        return result

