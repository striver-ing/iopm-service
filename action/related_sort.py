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

class RelatedSort():
    ZERO_CLASSIFY = 1
    FIRST_CLASSIFY = 2
    SECOND_CLASSIFY = 3

    HOT_FACTOR = 'hot_factor'
    CLUES_FACTOR = 'clues_factor'

    def __init__(self):
        self._oracledb = OracleDB()
        self._clues = {}
        self._classify = {
            RelatedSort.ZERO_CLASSIFY:{},
            RelatedSort.FIRST_CLASSIFY:{},
            RelatedSort.SECOND_CLASSIFY:{}
        }
        self._relacted_factor = {
            RelatedSort.HOT_FACTOR : 0,
            RelatedSort.CLUES_FACTOR : 0
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
            self._classify[RelatedSort.ZERO_CLASSIFY][classify_id] = classify_weight

    def get_classify_weigth(self, classify_id, classify_rank = ZERO_CLASSIFY):
        return self._classify[classify_rank][classify_id]

    def load_related_factor(self):
        sql = 'select t.hot_factor, t.clues_factor from TAB_IOPM_RELATED_FACTOR t'
        related_factor = self._oracledb.find(sql)
        if related_factor:
            self._relacted_factor[RelatedSort.HOT_FACTOR] = related_factor[0][0]
            self._relacted_factor[RelatedSort.CLUES_FACTOR] = related_factor[0][1]

    def get_related_factor(self, factor_type):
        '''
        @summary: 取相关系数
        ---------
        @param factor_type: RelatedSort.HOT_FACTOR  RelatedSort.CLUES_FACTOR
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

    def get_hot_related_weight(self, hot_id):
        '''
        @summary: 计算涉我热点权重
        ---------
        @param hot_id:
        ---------
        @result:
        '''

        sql = 'select t.hot, t.clues_id from TAB_IOPM_HOT_INFO t where t.id = %d'%hot_id
        hot_info = self._oracledb.find(sql)
        if hot_info:
            hot_value = hot_info[0][0] / 100
            clues_id = hot_info[0][1]   # 此处可能更改能按热点相关的文章所匹配到的线索id

            F = hot_value * self.get_related_factor(RelatedSort.HOT_FACTOR) + self.get_A(clues_id) * self.get_related_factor(RelatedSort.CLUES_FACTOR)

            return F * 100

        else:
            log.error('TAB_IOPM_HOT_INFO 无 hot_id = %d,  sql = %s'%(hot_id, sql))
            return 0

    def get_article_releated_weight(self, article_id):
        '''
        @summary: 计算涉我舆情权重
        ---------
        @param article_id:
        ---------
        @result:
        '''
        article_weight = 0

        sql = 'select t.clues_ids from TAB_IOPM_ARTICLE_INFO t where id = %d'%article_id
        clue_ids = self._oracledb.find(sql) #[('160',)] 或 []
        if clue_ids:
            clue_ids = clue_ids[0][0]
            print(clue_ids)
            article_weight = self.get_A(clue_ids)

        return article_weight

if __name__ == '__main__':
    related_sort = RelatedSort()
    a = related_sort.get_hot_related_weight(130215)
    print(a)

    b = related_sort.get_article_releated_weight(503344)
    print(b)