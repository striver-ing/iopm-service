# -*- coding: utf-8 -*-
'''
Created on 2017-08-02 09:20
---------
@summary: 配置
---------
@author: Boris
'''

# url映射配置


# Turn on/off debugging
DEBUG = False

URLS = (
    '/related_sort', 'action.related_sort_action.RelatedSortAction',
    '/es', 'action.elastic_search_action.ElasticSearchAction',
    '/(.*)', 'action.help.Help'
)

API_PORT = 8080