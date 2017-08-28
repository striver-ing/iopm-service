# -*- coding: utf-8 -*-
'''
Created on 2017-08-23 13:44
---------
@summary:
---------
@author: Boris
'''

import sys
sys.path.append('../')
import utils.tools as tools
from utils.log import log
from db.elastic_search import ES

class ElasticSearchServer():
    def __init__(self):
        self._es = ES('192.168.60.40')
        # self._es = ES('localhost')


    def search(self, table, body):
        return self._es.search(table, body)