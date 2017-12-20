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

    HOT_FACTOR = 401
    CLUES_FACTOR = 402
    NEGATIVE_EMOTION_FACTOR = 403
    VIP_FACTOR = 404

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
            RelatedSortService.CLUES_FACTOR : 0,
            RelatedSortService.NEGATIVE_EMOTION_FACTOR : 0,
            RelatedSortService.VIP_FACTOR : 0
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
        sql = 'select factor, t.value from TAB_IOPM_RELATED_FACTOR t'
        related_factors = self._oracledb.find(sql)
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
        # c1j、c2b、c3d 为命中线索的权重
        # c4 为 c4分类的平均权重
        # 即A的分子为命中线索的权重总和分母为命中线索的权重总和 加上 未命中的分类平均权重的总和
        # V = 相关报道主流媒体总数 / 相关报道总数
        # E = 相关报道负面情感总数 / 相关报道总数

    @tools.log_function_time
    def get_A(self, clue_ids):
        '''
        @summary: 计算线索综合权重
        ---------
        @param clues_ids: 多个线索id逗号分隔 类型为字符串； 或单个线索id
        ---------
        @result:
        '''
        if not clue_ids:
            return 0

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

    @tools.log_function_time
    def get_hot_related_weight(self, hot_id, hot_value = None, clues_id = '', article_count = None, vip_count = None, negative_emotion_count = None):
        '''
        @summary: 计算涉我热点权重
        ---------
        @param hot_id: 热度id
        @param hot_value: 热度值 int
        @param clues_id: 线索id 字符串 或 单个id
        ---------
        @result:
        '''
        if hot_value != None:
            hot_value = hot_value / 100
            clues_id = clues_id #or self.get_hot_article_clue_ids(hot_id)
            # clues_id = self.get_hot_article_clue_ids(hot_id)

            F = hot_value * self.get_related_factor(RelatedSortService.HOT_FACTOR) + self.get_A(clues_id) * self.get_related_factor(RelatedSortService.CLUES_FACTOR) + self.get_V(article_count, vip_count) * self.get_related_factor(RelatedSortService.VIP_FACTOR) + self.get_E(article_count, negative_emotion_count) * self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR)

            #print(hot_value ,'*', self.get_related_factor(RelatedSortService.HOT_FACTOR), '+', self.get_A(clues_id), '*', self.get_related_factor(RelatedSortService.CLUES_FACTOR), '+', self.get_V(article_count, vip_count), '*', self.get_related_factor(RelatedSortService.VIP_FACTOR), '+', self.get_E(article_count, negative_emotion_count), '*', self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR))

            return F * 100

        else:
            sql = 'select t.hot, t.clues_id, t.NEGATIVE_EMOTION_COUNT, t.is_vip, t.ARTICLE_COUNT from TAB_IOPM_HOT_INFO t where t.id = %d'%hot_id
            hot_info = self._oracledb.find(sql)
            if hot_info:
                hot_value = hot_info[0][0] / 100
                # clues_id = hot_info[0][1]   # 此处可能更改能按热点相关的文章所匹配到的线索id
                negative_emotion_count = hot_info[0][2]
                vip_count = hot_info[0][3]
                article_count = hot_info[0][4]

                clues_id = self.get_hot_article_clue_ids(hot_id)

                F = hot_value * self.get_related_factor(RelatedSortService.HOT_FACTOR) + self.get_A(clues_id) * self.get_related_factor(RelatedSortService.CLUES_FACTOR) + self.get_V(article_count, vip_count) * self.get_related_factor(RelatedSortService.VIP_FACTOR) + self.get_E(article_count, negative_emotion_count) * self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR)

                return F * 100

            else:
                log.error('TAB_IOPM_HOT_INFO 无 hot_id = %d,  sql = %s'%(hot_id, sql))
                return -1

    @tools.log_function_time
    def get_article_releated_weight(self, article_id = None, clue_ids = '', may_invalid = None, vip_count = None, negative_emotion_count = None, article_count = 1):
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

        if clue_ids:
            article_weight = self.get_A(clue_ids) + self.get_V(article_count, vip_count) * self.get_related_factor(RelatedSortService.VIP_FACTOR) + self.get_E(article_count, negative_emotion_count) * self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR)

            return article_weight if may_invalid else article_weight * 100 # 可能是@  # 等无效的数据，那么权重0~1

        else:
            sql = 'select t.clues_ids, t.may_invalid, t.is_vip, t.emotion from TAB_IOPM_ARTICLE_INFO t where id = %d'%article_id
            clues = self._oracledb.find(sql) #[('160',)] 或 []
            if clues:
                clue_ids = clues[0][0]
                may_invalid = clues[0][1]
                vip_count = clues[0][2] or 0
                negative_emotion_count = (clues[0][3] == 2) and 1 or 0

                article_weight = self.get_A(clue_ids) + self.get_V(article_count, vip_count) * self.get_related_factor(RelatedSortService.VIP_FACTOR) + self.get_E(article_count, negative_emotion_count) * self.get_related_factor(RelatedSortService.NEGATIVE_EMOTION_FACTOR)

                return article_weight if may_invalid else article_weight * 100 # 可能是@  # 等无效的数据，那么权重0~1

            else:
                log.error('TAB_IOPM_ARTICLE_INFO 无 id = %d,  sql = %s'%(article_id, sql))
                return -1

    def deal_hot(self, hot_id, hot_value = 0, clues_id = '', is_update_db = False, article_count = None, vip_count = None, negative_emotion_count = None):
        hot_weight = self.get_hot_related_weight(hot_id, hot_value = hot_value, clues_id = clues_id, article_count = article_count, vip_count = vip_count, negative_emotion_count = negative_emotion_count)
        self._oracledb.close()

        if hot_weight != -1:
            return True, hot_weight
        else:
            return False, hot_weight

    def deal_article(self, article_id, clue_ids = '', may_invalid = None, is_update_db = False, vip_count = None, negative_emotion_count = None, article_count = 1):
        article_weight = self.get_article_releated_weight(article_id, clue_ids, may_invalid, vip_count, negative_emotion_count)
        self._oracledb.close()

        if article_weight != -1:
            return True, article_weight
        else:
            return False, article_weight

if __name__ == '__main__':
    related_sort = RelatedSortService()
    a = related_sort.deal_hot(2690862, hot_value = 23, clues_id = '278', is_update_db = False, article_count = 3, vip_count = 3, negative_emotion_count = 0)
    print(a)


    # b = related_sort.get_article_releated_weight(1123802)
    # print(b)

    # related_sort.load_related_factor()
    # print(related_sort.get_related_factor(RelatedSortService.CLUES_FACTOR))
    # print(related_sort.get_related_factor(RelatedSortService.HOT_FACTOR))
    print(0.23 * 0.3 + 0.25 * 0.7 + 0.2* 1 +  0.5 *0)