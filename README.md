涉广电舆情接口说明
====
1.获取全国热点分析结果
----------

接口：hotspot_al/interface/getHotAnalysis

参数：

    period:1 (周期：1-近24H；7-近7天；)

返回值：

    {
        message: "查询成功",//结果说明
        status: 1,//接口返回状态0,失败；1，成功
        data: [ 
        {
            "kw":"最高法副院长山东调研",//热点或敏感词
            "hot":100,//热度
            "infoId":["1","2","3"]//相关信息的信息id
        },
        {},
        ……
    ]
    }

2.获取涉我热点分析结果
----------

接口：hotspot_al/interface/getHotAnalysis_self

参数：

    period:1 (周期：1-近24H；7-近7天；)

返回值：

    {
        message: "查询成功",//结果说明
        status: 1,//接口返回状态0,失败；1，成功
        data: [ 
            {
                "88800": {//线索id
                    "num": 12,//线索相关数据量
                    "data": [//线索相关热点
                        {
                            "kw": "上海市文化广播影视管理局老干部活动中心",//热点
                            "kg": "上海市 文化 广播 影视 管理局 老干部 活动中心",//热词
                            "hot": 8//热度值
                        },{},……
                     ]
                },
                cluesId:{
                    "num": 12,
                    "data": [{},{})]
                }
            }
        ]
    }

3. 获取全国热点相关报道
-------------

接口：hotspot_al/interface/getHotRelateInfo

参数：

    ids : 3444257605485313,3444265865282304,3444266404823808

返回值：

    {
        message: "查询成功",//结果说明
        status: 1,//接口返回状态0,失败；1，成功
        data: [ 
            {
                "title": "xxx", 
                "content": "xxx", 
                "author": "xxx", 
                "site": "xxx", 
                "url": "xxx", 
                "type": 1,//1，新闻；暂无其他数据类型
                "pubtime": "yyyy-MM-dd HH:mm:ss",
                "data_id": "xxx"
            },
            ……
        ]
    }

4. 获取微博热点信息--根据互动量判断
--------------------

接口：hotspot_al/interface/getWeiboHotInfo

参数：

    sTime:开始时间 yyyy-MM-dd HH:mm:ss
    eTime:结束时间 yyyy-MM-dd HH:mm:ss
    pageNo:起始页
    pageSize:每页获取的条数

返回值：

    {
        message: "查询成功",//结果说明
        status: 1,//接口返回状态0,失败；1，成功
        data: [
            {
                "content": "xxx", //内容
                "interaction_num": "xxx", //互动量
                "author": "xxx", //博主
                "rttcount": "xxx", //转发量
                "commtcount": "xxx", //评论量
                "pubtime": "yyyy-MM-dd HH:mm:ss",
                "url": "xxx"//源链接
            },
            {},{},……
        ]
    }

5. 获取微信热点信息--根据互动量判断
--------------------

接口：hotspot_al/interface/getWechatHotInfo

参数：

    sTime:开始时间 yyyy-MM-dd HH:mm:ss
    eTime:结束时间 yyyy-MM-dd HH:mm:ss
    pageNo:起始页
    pageSize:每页获取的条数

返回值：

    {
        message: "查询成功",
        status: 1, 接口返回状态0,失败；1，成功
        data: [
            {
                "title": "xxx", //标题
                "interaction_num": "xxx", //互动量
                "author": "xxx", //账号名
                "review_count": "xxx", //阅读量
                "up_count": "xxx", //点赞量
                "pubtime": "yyyy-MM-dd HH:mm:ss",
                "url": "xxx"//源链接
                },
                {},{},
                ……
        ]
    } 

6. 智能推荐舆情信息接口
-------------

接口：hotspot_al/interface/getCluesDataSearchInfo

参数：

    "infoType":1,//信息类型 0，全部；1，新闻；2，微信；3，微博；4，论坛；7，app；8，视频
    "emotion":0,//情感倾向 0，全部；1，正面；2,负面；3，中立
    "keywords":"**** ****",//关键词，空格隔开表示与的关系
    "sTime":"yyyy-MM-dd HH:mm:ss",//发布时间—开始时间
    "eTime":"yyyy-MM-dd HH:mm:ss",//发布时间—结束时间
    "data_ids":14754,25841,36914,//信息id
    "clus_ids":0,//线索库id,可传多个，不同id用英文逗号","隔开
    "sort":1,//排序字段 1,发布时间;2,评论量;默认是1
    "pageNo":1,
    "pageSize":10

返回值：

    {
        "message": "查询记录为0",
        "status": 1,
        "data": {
            "total": 0,//数据总量
            "data": [
                {
                    pubtime: "2017-07-14 16:23:08",//发布时间
                    picture: null,//图片地址
                    content: "",//内容
                    author: null,//作者
                    websiteName: "youth.cn",//站点名
                    title: "",//标题
                    host: "youth.cn",//网站域名
                    upCount: null,//点赞量
                    reviewCount: null,//阅读量
                    account: null,//账号
                    type: "1",
                    commtcount: null,//评论量
                    url: "http://news.youth.cn/jsxw/201707/t20170714_10296859.htm",
                    emotion: "1",//情感：1，正面；2，负面；3，中立
                    keywordAndIds:"{\"中央电视台\":\"88758\"}",
                    keywords:"中央电视台",
                    cluesIds:"88758"
                },{}……
            ]
        }
    }
       