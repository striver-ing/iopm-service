涉广电舆情接口说明
====
1.热点及舆情相关性排序
----------

接口：/related_sort

热点参数：

    hot_id:1                   # 热点id
    hot_value：80              # 热度值
    clues_id：12,13,14         # 相关舆情匹配到的线索id
    article_count              # 文章总数
    vip_count：1               # 主流媒体数
    negative_emotion_count ：  # 负面情感数
    is_update_db:1             # 是否更新数据库  0 否 1 是； 默认 否
    
舆情参数：

    article_id:1               # 线索id
    clues_ids：12,13,14        # 线索ids 
    may_invalid：1             # 是否可能无效
    vip_count：1               # 主流媒体数
    negative_emotion_count ：  # 负面情感数
    is_update_db:1             # 是否更新数据库  0 否 1 是； 默认 否

返回值：

    {
        'status' : 1 或 0,
        'message' : '处理成功'或 '处理失败',
        'id' : 热点id 或 文章id,
        'weight' : 权重
    }


### 算法描述 ###
>热度计算公式：F(相关性) = α * H + β * A + γ * V + δ * E
 
    注：
        F: 热度相关性
        α：热度系数
        β：线索系数
        γ：主流媒体系数
        δ: 负面情感系数
        H：热度
        A：线索综合权重
        V：主流媒体综合权重
        E: 负面情感综合权重
        α + β + γ + δ = 1

        A = (c1j  + c2b + c3d + ..... )/ c1j  + c2b + c3d + c4...
        c1j、c2b、c3d 为命中线索的权重
        c4 为 c4分类的平均权重
        即A的分子为命中线索的权重总和分母为命中线索的权重总和 加上 未命中的分类平均权重的总和
        V = 相关报道主流媒体总数 / 相关报道总数
        E = 相关报道负面情感总数 / 相关报道总数

伪代码：

>预加载

    def load_clues_weight(self):
        '''
        @summary: 将线索权重加载到缓存
        ---------
        ---------
        @result:
        '''
        # 查询数据库
        # 将结果保存在字典中

    def get_clue_weight(self, clue_id):
        '''
        @summary: 从缓存中直接取线索权重
        ---------
        @param clue_id:
        ---------
        @result:
        '''

        # 从字典表中取数据

    def load_classify_weight(self):
        '''
        @summary: 加载分类权重
        ---------
        ---------
        @result:
        '''
        # 查询数据库
        # 将结果保存在字典中

    def get_classify_weigth(self, classify_id, classify_rank = FIRST_CLASSIFY):
         '''
        @summary: 取分类权重，默认是一级
        ---------
        ---------
        @result:
        '''

        # 从字典表中取数据

    def load_related_factor(self):
        '''
        @summary: 加载相关系数
        ---------
        @param factor_type: RelatedSortService.HOT_FACTOR  RelatedSortService.CLUES_FACTOR
        ---------
        @result:
        '''
        # 查询数据库
        # 将结果保存在字典中
        
    def get_related_factor(self, factor_type):
        '''
        @summary: 取相关系数
        ---------
        @param factor_type: RelatedSortService.HOT_FACTOR  RelatedSortService.CLUES_FACTOR
        ---------
        @result:
        '''

        # 从字典表中取数据

>计算线索综合权重

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

        # 取没有匹配到的分类的平均权重 如c4 c5
        sql = '''
            select distinct(zero_id) from TAB_IOPM_CLUES t where t.zero_id not in (
                   select distinct(zero_id) from TAB_IOPM_CLUES t where t.id in ({clue_ids})
            ) and t.zero_id != 7
        '''.format(clue_ids = clue_ids)

        #执行sql
        # 计算各个分类平均权重的总和classify_weight 如c4+c5
    
        # 将clue_ids 按逗号拆开，遍历计算线索权重总和clues_weight 如c1j  + c2b + c3d
        for clue_id in clue_ids.split(','):
            clues_weight += self.get_clue_weight(int(clue_id))

        A = clues_weight / (clues_weight + classify_weight)

        return A

>计算主流媒体综合权重

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

>计算负面情感综合权重

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


>计算涉我热点权重

    def get_hot_related_weight(self, hot_id):
        '''
        @summary: 计算涉我热点权重
        ---------
        @param hot_id:
        ---------
        @result:
        '''

        # 根据hot_id取该热点的热度值及线索id
        if 存在:
            hot_value = 热度值 / 100
            clues_id = 线索id   # 此处可能更改成按热点相关的文章所匹配到的线索id

            F = 热度值 * 热度系数 + 线索综合权重 * 线索系数 + 主流媒体系数 * 主流媒体综合权重 + 负面系数 * 负面综合权重

            return F * 100

        else:
            return -1

>计算涉我舆情权重

    def get_article_releated_weight(self, article_id):
        '''
        @summary: 计算涉我舆情权重
        ---------
        @param article_id:
        ---------
        @result:
        '''
        article_weight = 0

        # 查询改舆情所匹配到的线索id和是否是@ #等无效的舆情clues
        if 存在:
            clue_ids = 线索ids
            may_invalid = 是否无效
            # 计算线索综合权重A
            article_weight = self.get_A(clue_ids)  + 主流媒体系数 * 主流媒体综合权重 + 负面系数 * 负面综合权重

            return article_weight*100 如果该舆情有效，否则返回article_weight。
            # 这样保证了有效的结果在1到100之间，可能无效的结果在0到1之间

        else:
            return -1

1.ES查询接口
----------
接口：/es

    例子（查询全部）：
    http://localhost:8080/es?table=tab_iopm_article_info&body={%22query%22:{%22match_all%22:{}}}

参数（post 或 get方式）：

    table:tab_iopm_article_info  
    body:{...}


返回值：json格式