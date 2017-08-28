# -*- coding: utf-8 -*-
'''
Created on 2017-08-09 15:44
---------
@summary: 相关性排序
---------
@author: Boris
'''
import sys
sys.path.append('../')
import utils.tools as tools
from utils.log import log
from db.oracledb import OracleDB

class RelatedSortService():
    ZERO_CLASSIFY = 1
    FIRST_CLASSIFY = 2
    SECOND_CLASSIFY = 3

    HOT_FACTOR = 'hot_factor'
    CLUES_FACTOR = 'clues_factor'

    def __init__(self):
        self._oracledb = OracleDB()
        self._clues = {}
        self._classify = {
            RelatedSortService.ZERO_CLASSIFY:{},
            RelatedSortService.FIRST_CLASSIFY:{},
            RelatedSortService.SECOND_CLASSIFY:{}
        }
        self._relacted_factor = {
            RelatedSortService.HOT_FACTOR : 0,
            RelatedSortService.CLUES_FACTOR : 0
        }

        self.load_clues_weight()
        self.load_classify_weight()
        self.load_related_factor()

    def load_clues_weight(self):
        '''
        @summary: 将线索权重加载到缓存
        ---------
        ---------
        @result:
        '''

        sql = 'select t.id, t.weight from TAB_IOPM_CLUES t'
        clues = self._oracledb.find(sql)
        for clue in clues:
            clue_id = clue[0]
            clue_weight = clue[1]
            self._clues[clue_id] = clue_weight

    def get_clue_weight(self, clue_id):
        '''
        @summary: 从缓存中直接取线索权重
        ---------
        @param clue_id:
        ---------
        @result:
        '''

        return self._clues[clue_id]

    def load_classify_weight(self):
        '''
        @summary: 加载分类权重
        ---------
        ---------
        @result:
        '''

        # 0级
        sql = 'select t.zero_id, avg(t.weight)from TAB_IOPM_CLUES t group by t.zero_id'
        classifys = self._oracledb.find(sql)
        for classify in classifys:
            classify_id = classify[0]
            classify_weight = classify[1]
            self._classify[RelatedSortService.ZERO_CLASSIFY][classify_id] = classify_weight

    def get_classify_weigth(self, classify_id, classify_rank = ZERO_CLASSIFY):
        return self._classify[classify_rank][classify_id]

    def load_related_factor(self):
        sql = 'select t.hot_factor, t.clues_factor from TAB_IOPM_RELATED_FACTOR t'
        related_factor = self._oracledb.find(sql)
        if related_factor:
            self._relacted_factor[RelatedSortService.HOT_FACTOR] = related_factor[0][0]
            self._relacted_factor[RelatedSortService.CLUES_FACTOR] = related_factor[0][1]

    def get_related_factor(self, factor_type):
        '''
        @summary: 取相关系数
        ---------
        @param factor_type: RelatedSortService.HOT_FACTOR  RelatedSortService.CLUES_FACTOR
        ---------
        @result:
        '''

        return self._relacted_factor[factor_type]

    ################################### 计算 相关性 #################################################
    # F(相关性) = α * H + β * A

    # 注：
    #     F:热度相关性
    #     α ：热度系数
    #     β：线索系数
    #     H：热度
    #     A：线索综合权重

    #     α + β = 1
    #     A = (c1j  + c2b + c3d + ..... )/ c1j  + c2b + c3d + c4...

    #     c1j、c2b、c3d 为命中线索的权重
    #     c4 为 c4分类的平均权重
    #     即分子为命中线索的权重总和
    #     分母为命中线索的权重总和 加上 未命中的分类平均权重的总和

    def get_A(self, clue_ids):
        '''
        @summary: 计算线索综合权重
        ---------
        @param clues_ids: 多个线索id逗号分隔 类型为字符串； 或单个线索id
        ---------
        @result:
        '''
        classify_weight = 0
        clues_weight = 0
        clue_ids = clue_ids if isinstance(clue_ids, str) else str(clue_ids)

        # 取没有匹配到的分类
        sql = '''
            select distinct(zero_id) from TAB_IOPM_CLUES t where t.zero_id not in (
                   select distinct(zero_id) from TAB_IOPM_CLUES t where t.id in ({clue_ids})
            ) and t.zero_id != 7
        '''.format(clue_ids = clue_ids)

        # print(sql)

        classify_ids = self._oracledb.find(sql) # [(6,), (4,), (5,), (3,)] 或 []
        if classify_ids:
            for classify_id in classify_ids:
                classify_weight += self.get_classify_weigth(classify_id[0])

        for clue_id in clue_ids.split(','):
            clues_weight += self.get_clue_weight(int(clue_id))

        A = clues_weight / (clues_weight + classify_weight)

        return A

    def get_hot_article_clue_ids(self, hot_id):
        '''
        @summary: 取热点相关舆情所涉及的线索ids
        ---------
        @param hot_id:
        ---------
        @result:
        '''

        sql = 'select t.clues_ids from TAB_IOPM_ARTICLE_INFO t where hot_id = %d'%hot_id
        results = self._oracledb.find(sql)

        clue_ids = set()
        for result in results:
            result_list = result[0].split(',')
            for result in result_list:
                clue_ids.add(result)

        clue_ids = ','.join(clue_ids)
        return clue_ids

    def get_hot_related_weight(self, hot_id, hot_value = 0, clues_id = ''):
        '''
        @summary: 计算涉我热点权重
        ---------
        @param hot_id: 热度id
        @param hot_value: 热度值 int
        @param clues_id: 线索id 字符串 或 单个id
        ---------
        @result:
        '''
        if hot_value:
            hot_value = hot_value / 100
            clues_id = clues_id or self.get_hot_article_clue_ids(hot_id)

            F = hot_value * self.get_related_factor(RelatedSortService.HOT_FACTOR) + self.get_A(clues_id) * self.get_related_factor(RelatedSortService.CLUES_FACTOR)

            return F * 100

        else:

            sql = 'select t.hot, t.clues_id from TAB_IOPM_HOT_INFO t where t.id = %d'%hot_id
            hot_info = self._oracledb.find(sql)
            if hot_info:
                hot_value = hot_info[0][0] / 100
                # clues_id = hot_info[0][1]   # 此处可能更改能按热点相关的文章所匹配到的线索id
                clues_id = self.get_hot_article_clue_ids(hot_id)

                F = hot_value * self.get_related_factor(RelatedSortService.HOT_FACTOR) + self.get_A(clues_id) * self.get_related_factor(RelatedSortService.CLUES_FACTOR)

                return F * 100

            else:
                log.error('TAB_IOPM_HOT_INFO 无 hot_id = %d,  sql = %s'%(hot_id, sql))
                return -1

    def get_article_releated_weight(self, article_id = None, clue_ids = '', may_invalid = None):
        '''
        @summary: 计算涉我舆情权重
        ---------
        @param article_id: 文章id
        @param clue_ids: 线索ids 多个线索id逗号分隔 类型为字符串； 或单个线索id
        @param may_invalid: 是否可能无效  整形
        ---------
        @result:
        '''

        article_weight = 0

        if clue_ids and may_invalid:
            article_weight = self.get_A(clue_ids)
            return article_weight if may_invalid else article_weight * 100 # 可能是@  # 等无效的数据，那么权重0~1

        else:
            sql = 'select t.clues_ids, t.may_invalid from TAB_IOPM_ARTICLE_INFO t where id = %d'%article_id
            clues = self._oracledb.find(sql) #[('160',)] 或 []
            if clues:
                clue_ids = clues[0][0]
                may_invalid = clues[0][1]
                article_weight = self.get_A(clue_ids)

                return article_weight if may_invalid else article_weight * 100 # 可能是@  # 等无效的数据，那么权重0~1

            else:
                log.error('TAB_IOPM_ARTICLE_INFO 无 id = %d,  sql = %s'%(article_id, sql))
                return -1

    def deal_hot(self, hot_id, hot_value = 0, clues_id = ''):
        hot_weight = self.get_hot_related_weight(hot_id, hot_value = hot_value, clues_id = clues_id)

        if hot_weight != -1:
            sql = 'update TAB_IOPM_HOT_INFO set weight = %s where id = %d'%(hot_weight, hot_id)
            return self._oracledb.update(sql), hot_weight

        else:
            return False, hot_weight

    def deal_article(self, article_id, clue_ids = '', may_invalid = None):
        article_weight = self.get_article_releated_weight(article_id, clue_ids, may_invalid)

        if article_weight != -1:
            sql = 'update TAB_IOPM_ARTICLE_INFO set weight = %s where id = %d'%(article_weight, article_id)
            return self._oracledb.update(sql), article_weight

        else:
            return False, article_weight

if __name__ == '__main__':
    related_sort = RelatedSortService()
    # a = related_sort.get_hot_related_weight(1123726)
    # print(a)

    b = related_sort.get_article_releated_weight(1123802)
    print(b)