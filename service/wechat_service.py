# -*- coding: utf-8 -*-
'''
Created on 2017-09-22 15:55
---------
@summary:
---------
@author: Boris
'''
import sys
sys.path.append('..')

from utils.log import log
import utils.tools as tools

HEADERR = {
    "Query": "String Parameters",
    "view": "URL encoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Cache-Control": "max-age=0",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "qyapi.weixin.qq.com"
}

class WechatService():
    def __init__(self, corpid, secret, agentid):
        self._agentid = agentid
        self._access_token = self.get_access_token(corpid, secret)

    def get_access_token(self, corpid, secret):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s'%(corpid, secret)
        result = tools.get_json_by_requests(url, headers = HEADERR)
        return result.get('access_token')

    def send_msg(self, users, title, time, content, article_url):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s'%self._access_token
        data = {
           "touser" : users,
           "toparty" : "",
           "totag" : "",
           "msgtype" : "textcard",
           "agentid" : self._agentid,
           "textcard" : {
                    "title" : title,
                    "description" : "<div class=\"gray\">{time}</div> <div class=\"normal\">{content}</div>".format(time = time, content = content),
                    "url" : article_url,
                    "btntxt":"详情"
           }
        }

        data = tools.dumps_json(data).encode('utf-8')
        result = tools.get_json_by_requests(url = url, headers = HEADERR, data = data )
        return result

    def upload_file(self, file_path, file_type = 'file'):
        '''
        @summary: 上传临时文件
        ---------
        @param file_path: 文件
        @param file_type: 媒体文件类型，分别有图片（image）、语音（voice）、视频（video），普通文件（file）
        ---------
        @result:
        '''
        url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s'%(self._access_token, file_type)
        result = tools.upload_file(url, file_path, file_type)

        return result.get('media_id')


    def send_file(self, users, media_id):
        '''
        @summary:
        ---------
        @param users:
        @param media_id: 文件id，可以调用上传临时素材接口获取
        ---------
        @result:
        '''
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s'%self._access_token
        data = {
           "touser" : users,
           "toparty" : "",
           "totag" : "",
           "msgtype" : "file",
           "agentid" : self._agentid,
           "file" : {
                "media_id" : media_id
           },
           "safe":0
        }

        data = tools.dumps_json(data).encode('utf-8')
        result = tools.get_json_by_requests(url = url, headers = HEADERR, data = data )
        return result

    def get_user(self, user_id):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=%s&userid=%s'%(self._access_token, user_id)
        result = tools.get_json_by_requests(url)
        return result

    def get_user_list(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=%s&department_id=1&fetch_child=1'%(self._access_token)
        result = tools.get_json_by_requests(url)
        # tools.print(result)
        return result

    def get_depertment(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token='+self._access_token
        result = tools.get_json_by_requests(url)
        tools.print(result)

    def get_tags(self):
        '''
        @summary:
        ---------
        ---------
        @result:
        '''
        url = 'https://qyapi.weixin.qq.com/cgi-bin/tag/list?access_token='+self._access_token
        result = tools.get_json_by_requests(url)
        tools.print(result)

if __name__ == '__main__':
    corpid = 'wwd1c26293d0353651'
    secret = 'e4nN9A5MN9yM1JY77-2oTk1i3H_2SWAw1saZ2X0ItuQ'
    wechat = WechatService(corpid, secret, 1000002)
    # wechat.get_user('ChenXinWei')
    # wechat.get_user_list()

    # title = '今天，为了这件大事，央视6位“名嘴”欢聚一堂！'
    # time = '2017-09-19 23:31:37'
    # content = '9月19日，2018年“CCTV国家品牌计划”发布会在京召开。本场发布会受到了社会各界的广泛关注...'
    # url = 'http://mp.weixin.qq.com/s?__biz=MTI0MDU3NDYwMQ==&mid=2656610975&idx=1&sn=e22e85b24d1ccbf0e55bfd810af49d7a&scene=0#wechat_redirect'
    # users = 'Liubo'
    # wechat.send_msg(users, title, time, content, url)
    # import requests
    # access_token = 'Hb9in2l7dyjen_HayYQFk_WWut3VyGw2s7j1MjAKkC6ktsoGA4Zw_8odNBl6yAIvFVnLP_ka7q-g-P10t_liZIuKAsL_qkOzEH68pM3S16hOoY8XNyq05iBBSwDLPxV2Qm3BphIgrmvlxKmjhVCLkG0CRzA8CE9aj3HJO1p3gNJ1Pgaepjuy50e9XnCxKbwN9aDn6nJbRsdLXR4OsHWs8Q'
    # file_type = 'file'
    # url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s'%(access_token, file_type)

    # result = requests.post(url, files=files)
    # print(result.text)

    media_id = wechat.upload_file('1.txt')#, is_stream = False)
    print(media_id)
    result = wechat.send_file('Liubo', media_id)
    print(result)


    file = open('1.txt', 'rb')
    print(file.read())

    # wechat.send_file('Liubo', '32bBsTPJ7M7XeQmHX4nmEo5y7RgYCLTHvnvtqQF7Emyo')