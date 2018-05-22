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
import threading

class RelatedSortService(threading.Thread):
    ZERO_CLASSIFY = 1
    FIRST_CLASSIFY = 2
    SECOND_CLASSIFY = 3

    HOT_FACTOR = 401
    CLUES_FACTOR = 402
    NEGATIVE_EMOTION_FACTOR = 403
    VIP_FACTOR = 404

    _db = OracleDB()

    def __init__(self):
        super(RelatedSortService, self).__init__()
        self._clues = {}
        self._clues_total_weight = 0
        self._classify = {
            RelatedSortService.ZERO_CLASSIFY:{},
            RelatedSortService.FIRST_CLASSIFY:{},
            RelatedSortService.SECOND_CLASSIFY:{}
        }
        self._relacted_factor = {
            RelatedSortService.HOT_FACTOR : 0,
            RelatedSortService.CLUES_FACTOR : 0,
            RelatedSortService.NEGATIVE_EMOTION_FACTOR : 0,
            RelatedSortService.VIP_FACTOR : 0
        }

        print('更新线索权重...')
        self.load_clues_weight()
        self.load_classify_weight()
        self.load_related_factor()

        print('更新线索权重完毕')

    def run(self):
        while True:
            tools.delay_time(60 * 60)  # 一小时后更细权重
            print('更新线索权重...')
            self.load_clues_weight()
            self.load_classify_weight()
            self.load_related_factor()

            print('更新线索权重完毕')

    def load_clues_weight(self):
        '''
        @summary: 将线索权重加载到缓存
        ---------
        ---------
        @result:
        '''

        sql = 'select t.id, t.weight from TAB_IOPM_CLUES t  where zero_id != 7'
        clues = RelatedSortService._db.find(sql)
        for clue in clues:
            clue_id = clue[0]
            clue_weight = clue[1]
            self._clues_total_weight += clue_weight
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
        sql = 'select t.zero_id, avg(t.weight)from TAB_IOPM_CLUES t where t.zero_id!=7 group by t.zero_id'
        classifys = RelatedSortService._db.find(sql)
        for classify in classifys:
            classify_id = classify[0]
            classify_weight = classify[1]
            self._classify[RelatedSortService.ZERO_CLASSIFY][classify_id] = classify_weight

    def get_classify_weigth(self, classify_id, classify_rank = ZERO_CLASSIFY):
        return self._classify[classify_rank][classify_id]

    def load_related_factor(self):
        sql = 'select factor, t.value from TAB_IOPM_RELATED_FACTOR t'
        related_factors = RelatedSortService._db.find(sql)
        # print(related_factors)
        if related_factors:
            for related_factor in related_factors:
                self._relacted_factor[related_factor[0]] = related_factor[1]

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
    # F(相关性) = α * H + β * A + γ * V + δ * E

    # 注：
        # F: 热度相关性
        # α：热度系数
        # β：线索系数
        # γ：主流媒体系数
        # δ: 负面情感系数
        # H：热度
        # A：线索综合权重
        # V：主流媒体综合权重
        # E: 负面情感综合权重

        # α + β + γ + δ = 1
        # A = (c1j  + c2b + c3d + ..... )/ c1j  + c2b + c3d + c4...
        # 修改 A = (匹配到的线索权重 线索不去重) / 线索权重总和
        # c1j、c2b、c3d 为命中线索的权重
        # c4 为 c4分类的平均权重
        # 即A的分子为命中线索的权重总和分母为命中线索的权重总和 加上 未命中的分类平均权重的总和
        # V = 相关报道主流媒体总数 / 相关报道总数
        # E = 相关报道负面情感总数 / 相关报道总数

    @tools.log_function_time
    def get_A(self, clue_ids, zero_ids):
        '''
        @summary: 计算线索综合权重
        ---------
        @param clues_ids：匹配到的多个线索id逗号分隔 类型为字符串；
        @param zero_ids: 匹配到的多个zero_id逗号分隔 类型为字符串
        ---------
        @result:
        '''
        if not clue_ids:
            return 0

        classify_weight = 0
        clues_weight = 0
        clue_ids = clue_ids if isinstance(clue_ids, str) else str(clue_ids)

        # # 取没有匹配到的分类
        # contained_classify_ids = zero_ids.split(',') #匹配到的zero id [6,5,4,3,2,1] 或 []
        # uncontained_classify_ids = [classify_id for classify_id in self._classify[RelatedSortService.ZERO_CLASSIFY].keys() if str(classify_id) not in contained_classify_ids]

        # for classify_id in uncontained_classify_ids:
        #     classify_weight += self.get_classify_weigth(classify_id)

        for clue_id in clue_ids.split(','):
            clues_weight += self.get_clue_weight(int(clue_id))

        # A = clues_weight / (clues_weight + classify_weight) if clues_weight + classify_weight > 0 else 0
        A = clues_weight / self._clues_total_weight
        print(clues_weight)
        print(self._clues_total_weight)
        return A * 10 # 太小了


    def get_V(self, article_count, vip_count):
        '''
        @summary: 主流媒体综合权重
        ---------
        @param article_count:文章总数
        @param vip_count:主流媒体总数
        ---------
        @result:
        '''
        if article_count:
            return (vip_count or 0) / article_count
        else:
            return 0

    def get_E(self, article_count, negative_emotion_count):
        '''
        @summary: 负面情感综合权重
        ---------
        @param article_count:文章总数
        @param negative_emotion_count:负面情感的文章总数
        ---------
        @result:
        '''
        if article_count:
            return (negative_emotion_count or 0) / article_count
        else:
            return 0

    @tools.log_function_time
    def get_hot_related_weight(self, hot_id, hot_value = None, clues_id = '', zero_ids = '', article_count = None, vip_count = None, negative_emotion_count = None):
        '''
        @summary: 计算涉我热点权重
        ---------
        @param hot_id: 热度id
        @param hot_value: 热度值 int
        @param clues_id: 线索id 字符串 或 单个id
        ---------
        @result:
        '''
        hot_value = hot_value / 100
        F = hot_value * self.get_related_factor(RelatedSortService.HOT_FACTOR) + self.get_A(clues_id, zero_ids) * self.get_related_factor(RelatedSortService.CLUES_FACTOR) + self.get_V(article_count, vip_count) * self.get_related_factor(RelatedSortService.VIP_FACTOR) + self.get_E(article_count, negative_emotion_count) * self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR)

        #print(hot_value ,'*', self.get_related_factor(RelatedSortService.HOT_FACTOR), '+', self.get_A(clues_id), '*', self.get_related_factor(RelatedSortService.CLUES_FACTOR), '+', self.get_V(article_count, vip_count), '*', self.get_related_factor(RelatedSortService.VIP_FACTOR), '+', self.get_E(article_count, negative_emotion_count), '*', self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR))

        return F * 100


    @tools.log_function_time
    def get_article_releated_weight(self, article_id = None, clue_ids = '', zero_ids = '', may_invalid = None, vip_count = None, negative_emotion_count = None, article_count = 1):
        '''
        @summary: 计算涉我舆情权重
        ---------
        @param article_id: 文章id
        @param clue_ids: 线索ids 多个线索id逗号分隔 类型为字符串； 或单个线索id
        @param may_invalid: 是否可能无效  整形
        ---------
        @result:
        '''

        article_weight = self.get_A(clue_ids, zero_ids) + self.get_V(article_count, vip_count) * self.get_related_factor(RelatedSortService.VIP_FACTOR) + self.get_E(article_count, negative_emotion_count) * self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR)
        return article_weight if may_invalid else article_weight * 100 # 可能是@  # 等无效的数据，那么权重0~1

    def deal_hot(self, hot_id, hot_value = 0, clues_id = '',zero_ids='', article_count = None, vip_count = None, negative_emotion_count = None):
        hot_weight = self.get_hot_related_weight(hot_id, hot_value = hot_value, clues_id = clues_id, zero_ids = zero_ids, article_count = article_count, vip_count = vip_count, negative_emotion_count = negative_emotion_count)

        if hot_weight != -1:
            return True, hot_weight
        else:
            return False, hot_weight # 不知道为啥是-1了  有时间看看

    def deal_article(self, article_id, clue_ids = '',zero_ids='', may_invalid = None, vip_count = None, negative_emotion_count = None, article_count = 1):
        article_weight = self.get_article_releated_weight(article_id, clue_ids, zero_ids, may_invalid, vip_count, negative_emotion_count)

        if article_weight != -1:
            return True, article_weight
        else:
            return False, article_weight

if __name__ == '__main__':
    #     "hot_value": 52.0,
    # "article_count": 8,
    # "clues_ids": "250,925,924,389,274,924,250,273,250,430,279,916,916,925,925,274,274,250,275,102,274,916,927,953,930,927,930,930,250,928,928,109,273,928",
    # "vip_count": 3,
    # "zero_ids": "6,2,5,7",
    # "negative_emotion_count": 8,
    # "hot_id": "f443d613-bc0e-330b-9643-7798e0c5ca97"
    related_sort = RelatedSortService()
    related_sort.start()
    clue_ids = '250,925,924,389,274,924,250,273,250,430,279,916,916,925,925,274,274,250,275,102,274,916,927,953,930,927,930,930,250,928,928,109,273,928'
    a = related_sort.deal_hot('25cd565c-4c0d-30a8-b853-21913e2dc6fa', hot_value = 52.0, clues_id = clue_ids, zero_ids = '6,2,5,7', article_count = 8, vip_count = 3, negative_emotion_count = 8)
    print(a)
    tools.delay_time(5)


    # # b = related_sort.get_article_releated_weight(1123802)
    # # print(b)

    # # related_sort.load_related_factor()
    # # print(related_sort.get_related_factor(RelatedSortService.CLUES_FACTOR))
    # # print(related_sort.get_related_factor(RelatedSortService.HOT_FACTOR))
    # print(0.23 * 0.3 + 0.25 * 0.7 + 0.2* 1 +  0.5 *0)
