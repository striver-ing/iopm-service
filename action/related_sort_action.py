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
import utils.tools as tools
import json

# {
#     'message':'热点及舆情推荐相关性排序处理中',
#     'status':1, # 未处理0  处理中1  处理完2
#     'total_count':200,
#     'deal_count':50
# }

class RelatedSortAction(object):
    _related_sort_service = RelatedSortService()
    _related_sort_service.start()

    def __init__(self):
        pass

    def GET(self):
        return self.deal_request()

    def POST(self):
        return self.deal_request()

    def deal_request(self):
        web.header('Content-Type','text/html;charset=UTF-8')
        print(str(web.input()))
        data = json.loads(json.dumps(web.input()))

        # 文章信息
        article_id = data.get('article_id')
        may_invalid = data.get('may_invalid') or 0

        # 热点信息
        hot_id = data.get('hot_id')
        hot_value = data.get('hot_value') or 0

        # 通用参数
        clues_ids = data.get('clues_ids') or ''
        article_count= data.get('article_count') or 0
        vip_count= data.get('vip_count') or 0
        negative_emotion_count = data.get('negative_emotion_count') or 0
        zero_ids = data.get('zero_ids') or ''

        status = 0 # 0 处理失败 1 处理成功
        weight = -1

        try:
            if hot_id:
                status, weight = RelatedSortAction._related_sort_service.deal_hot(hot_id, float(hot_value), clues_ids, zero_ids, int(article_count), int(vip_count), int(negative_emotion_count))

            elif article_id:
                status, weight = RelatedSortAction._related_sort_service.deal_article(article_id, clues_ids, zero_ids, int(may_invalid), int(vip_count), int(negative_emotion_count))

        except Exception as e:
            log.error(e)

        result = {
            "status" : 1 if status else 0,
            "message" : "处理成功" if status else "处理失败",
            "id":hot_id or article_id,
            "weight":weight
        }

        return tools.dumps_json(result)

