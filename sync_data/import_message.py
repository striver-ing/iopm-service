# -*- coding: utf-8 -*-
'''
Created on 2017-07-28 14:28
---------
@summary: 同步智能推荐的舆情信息
---------
@author: Boris
'''

import sys
sys.path.append('../')
import utils.tools as tools
from utils.export_data import ExportData
from db.oracledb import OracleDB

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Host": "192.168.60.38:8001"
}

db = OracleDB()
export_data = ExportData()

def get_datas():
    root_url = 'http://192.168.60.38:8001/hotspot_al/interface/getCluesDataSearchInfo?pageNo=%d&pageSize=100'
    # root_url = 'http://192.168.60.38:8001/hotspot_al/interface/getCluesDataSearchInfo?pageNo=%d&pageSize=100&sTime=2017-08-06 00:00:00&eTime=2017-08-06 23:59:59'

    count = 0
    page = 1
    while True:
        url = root_url%page

        datas = tools.get_json_by_requests(url, headers = HEADERS)
        if datas['message'] == '查询记录为0':
            print('每页100条  第%d页无数据 共导出 %d 条数据'%(page, count))
            break

        messages = datas['data']['data']
        for msg in messages:
            weight = 0 # 权重
            clues_ids = msg['cluesIds']

            # 取id
            sql = 'select SEQ_IOPM_ARTICLE.nextval from dual'
            article_id = db.find(sql)[0][0]

            def export_callback(execute_type, sql):
                if execute_type != ExportData.EXCEPTION:
                    for clues_id in clues_ids.split(','):
                        print(clues_id)
                        key_map = {
                            'id':'vint_sequence.nextval',
                            'article_id':'vint_%d'%article_id,
                            'clues_id':'vint_%s'%clues_id
                        }
                        export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_ARTICLE_CLUES_SRC', unique_key = 'url', datas = [{}])



            key_map = {
                'id':'vint_%d'%article_id,
                'account': 'str_account',
                'author': 'str_author',
                'clues_ids': 'str_cluesIds',
                'comment_count': 'int_commtcount',
                'content': 'clob_content',
                'emotion': 'int_emotion',
                'host': 'str_host',
                'keywords': 'str_keywords',
                'image_url': 'str_picture',
                'release_time': 'date_pubtime',
                'review_count': 'int_reviewCount',
                'title': 'str_title',
                'info_type': 'int_type',
                'up_count': 'int_upCount',
                'url': 'str_url',
                'uuid': 'str_uuid',
                'website_name': 'str_websiteName',
                'MAY_INVALID':'int_mayInvalid',
                'KEYWORD_CLUES_ID':'str_keywordAndIds',
                'keywords_count':'vint_%d'%len(msg['keywords'].split(','))
            }

            if not msg['url']:
                print(msg['title'])
                continue

            export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_ARTICLE_INFO', unique_key = 'url', datas = msg, callback = export_callback)
            count += 1

        page += 1

def main():
    get_datas()



if __name__ == '__main__':
    main()
