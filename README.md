涉广电舆情接口说明
====
1.热点及舆情相关性排序
----------

### 1.1 接口：/related_sort ###

热点参数：

    hot_id:1                   # 热点id
    hot_value：80              # 热度值
    clues_id：12,13,14         # 相关舆情匹配到的线索id
    article_count              # 文章总数
    vip_count：1               # 主流媒体数
    negative_emotion_count ：  # 负面情感数
    zero_ids:1,2,3             # 匹配到的一级类别

舆情参数：

    article_id:1               # 线索id
    clues_ids：12,13,14        # 线索ids
    may_invalid：1             # 是否可能无效
    vip_count：1               # 主流媒体数
    negative_emotion_count ：  # 负面情感数
    zero_ids:1,2,3             # 匹配到的一级类别

返回值：

    {
        'status' : 1 或 0,
        'message' : '处理成功'或 '处理失败',
        'id' : 热点id 或 文章id,
        'weight' : 权重
    }


### 1.2算法描述 ###
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

2.ES查询接口
----------
### 2.1接口：/es ###

    例子（查询全部）：
    http://localhost:8080/es?table=tab_iopm_article_info&body={%22query%22:{%22match_all%22:{}}}

**参数说明**（post 或 get方式）：

    table:tab_iopm_article_info
    body:{...}


返回值：json格式

3.微信推送接口
--------
### 3.1查询用户信息接口：/wechat/get_user_list ###

返回:

    {
    "errcode": 0,
    "errmsg": "ok",
    "userlist": [
        {
            "userid": "zhangsan",
            "name": "李四",
            "department": [1, 2],
            "order": [1, 2],
            "position": "后台工程师",
            "mobile": "15913215421",
            "gender": "1",
            "email": "zhangsan@gzdev.com",
            "isleader": 0,
            "avatar":           "http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/0",
            "telephone": "020-123456",
            "english_name": "jackzhang",
            "status": 1,
            "extattr": {"attrs":[{"name":"爱好","value":"旅游"},{"name":"卡号","value":"1234567234"}]}
        }
    ]
}

### 3.2推送消息接口：/wechat/send_msg ###

**参数说明**

    {
        "title":"xxxx",
        "time":"yyyy-mm-dd hh24-mi-dd",
        "content":"xxxxx...", //截取100字节
        "url":"http://www.xxxxx",
        "users":"UserID1|UserID2" // 多个userid用“|”分开， 全部发送@all
        //"users":"@all"  全部
    }

返回:

    {
       "errcode" : 0, // 0 表示成功
       "errmsg" : "ok",
       "invaliduser" : "UserID1", // 不区分大小写，返回的列表都统一转为小写
       "invalidparty" : "PartyID1",
       "invalidtag":"TagID1"
    }

### 3.3 推送文件接口 /wechat/send_file ###


**参数说明**

    {
        "file_path":"文件的共享路径"
        "users":"UserID1|UserID2" // 多个userid用“|”分开， 全部发送@all
        //"users":"@all"  全部
    }

返回:

    {
       "errcode" : 0, // 0 表示成功
       "errmsg" : "ok",
       "invaliduser" : "UserID1", // 推送失败的用户
    }

### 3.4 添加用户接口 ###

**请求方式**:POST(**HTTP**)

**请求地址**：http：//ip地址:8080/wechat/add_user

**请求包体：**

    {
       "user_id": "Zhangsan",
       "name": "张三",
       "mobile": "15913215421",
       "email": "zhangsan@gzdev.com",
       "enable":1
    }

**参数说明：**

| 参数 | 必须 | 说明 |
|:----|:---- |:-----|
|user_id|否|成员id 空时自动用uuid填充|
|name|是|成员名称。长度为1~64个字符， 必填|
|mobile|否|手机号码。企业内必须唯一，mobile/email二者不能同时为空|
|meail|否|邮箱。长度不超过64个字节，且为有效的email格式。企业内必须唯一，mobile/email二者不能同时为空|
|enable|否|启用/禁用成员。1表示启用成员，0表示禁用成员。默认为1|


**返回结果：**

    {
       "errcode": 0,
       "errmsg": "created",
       'user_id': "Zhangsan"
    }

**参数说明：**

| 参数 | 说明 |
|:----|:-----|
|errcode|返回码 （0 为成功， 非0 出错）|
|errmsg|对返回码的文本描述内容|
|user_id|成员id|


### 3.5 更新用户接口 ###
**请求方式**:POST(**HTTP**)

**请求地址**：http：//ip地址:8080/wechat/update_user

**请求包体：**

    {
       "user_id": "Zhangsan",
       "name": "李四",
       "mobile": "15913215421",
       "email": "zhangsan@gzdev.com",
       "enable":1
    }

**参数说明：**

| 参数 | 必须 | 说明 |
|:----|:---- |:-----|
|user_id|是|成员id|
|name|是|成员名称。长度为1~64个字符|
|mobile|是|手机号码。企业内必须唯一，mobile/email二者不能同时为空|
|meail|是|邮箱。长度不超过64个字节，且为有效的email格式。企业内必须唯一，mobile/email二者不能同时为空|
|enable|是|启用/禁用成员。1表示启用成员，0表示禁用成员|


**返回结果：**

    {
       "errcode": 0,
       "errmsg": "updated",
    }

**参数说明：**

| 参数 | 说明 |
|:----|:-----|
|errcode|返回码 （0 为成功， 非0 出错）|
|errmsg|对返回码的文本描述内容|


### 3.6 删除用户接口 ###
**请求方式**:POST/GET(**HTTP**)

**请求地址**：http：//ip地址:8080/wechat/del_user

**请求包体：**

    {
       "user_id": "Zhangsan"
    }

**参数说明：**

| 参数 | 必须 | 说明 |
|:----|:---- |:-----|
|user_id|是|成员id|


**返回结果：**

    {
       "errcode": 0,
       "errmsg": "deleted",
    }

**参数说明：**

| 参数 | 说明 |
|:----|:-----|
|errcode|返回码 （0 为成功， 非0 出错）|
|errmsg|对返回码的文本描述内容|

### 4.格式化关键词接口 ###
--------

>处理关键词乘积关系 如（a|b）(c) 处理成 a&b,a&c
>处理中英文逗号 如 hello word 你好 处理成 hello word&你好
>`&`代表与`,`代表或

### 4.1接口：/format_keywords ###

参数：keywords

请求方式： POST/GET

    例子：
    http://192.168.60.30:8080/format_keywords?keywords=hello word 你好
    返回：
    hellow word&你好

