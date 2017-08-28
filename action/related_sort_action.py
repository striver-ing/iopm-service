# -*- coding: utf-8 -*-
'''
Created on 2017-08-02 09:24
---------
@summary: 热点相关性排序
---------
@author: Boris
'''
import web
from service.related_sort_service import RelatedSortService
from utils.log import log
import json

# {
#     'message':'热点及舆情推荐相关性排序处理中',
#     'status':1, # 未处理0  处理中1  处理完2
#     'total_count':200,
#     'deal_count':50
# }

class RelatedSortAction(object):
    def __init__(self):
        self._related_sort_service = RelatedSortService()

    def GET(self):
        web.header('Content-Type','text/html;charset=UTF-8')
        print(str(web.input()))
        data = json.loads(json.dumps(web.input()))

        # 文章信息
        article_id = data.get('article_id')
        clue_ids = data.get('clue_ids')
        may_invalid = data.get('may_invalid') or 0

        # 热点信息
        hot_id = data.get('hot_id')
        hot_value = data.get('hot_value') or 0
        clues_id = data.get('clues_id') or ''

        status = 0 # 0 处理失败 1 处理成功
        weight = -1


        try:
            if hot_id:
                status, weight = self._related_sort_service.deal_hot(int(hot_id), int(hot_value), clues_id)

            elif article_id:
                status, weight = self._related_sort_service.deal_article(int(article_id), clue_ids, int(may_invalid))

        except Exception as e:
            log.error(e)

        result = {
            'status' : 1 if status else 0,
            'message' : '处理成功, 已更新数据库' if status else '处理失败',
            'id':hot_id or article_id,
            'weight':weight
        }

        return result

