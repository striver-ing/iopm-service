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

class SendMsgToWechatService():
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
        url = 'https://qyapi.weixin.qq.com/cgi-bin/tag/list?access_token='+self._access_token
        result = tools.get_json_by_requests(url)
        tools.print(result)

if __name__ == '__main__':
    # corpid = 'wwd1c26293d0353651'
    # secret = 'e4nN9A5MN9yM1JY77-2oTk1i3H_2SWAw1saZ2X0ItuQ'
    # send_msg = SendMsgToWechatService(corpid, secret)
    # # access_token = 'ee2OT8_dxxveCPUOYy16jcwzqYFiZNx1Odcd2YYuHNa2BTJzO8nwlSyZFaOZkozsiEkuUWlf62FdqTOTpX7sbOIwm0Th459qpKPp2S-SoKmocQOYv0_hEMjXO6XNHTKbJGtk7cI2DQw4O9p6-jeU12FaorqvMelfmDs2lA1Xbj9Aij1yJUFkQ-xcibnbfOYSt_T5uKM86-E1J1ldvq2WlXBEVwwvlKg-VNId4Vmo62F5aawzRVLCl37PMwwQh8VYeydfyG0xCmcEBv0gjYH0TnoRof-NtolArwf_TaW6W98'


    # send_msg.get_user('ChenXinWei')
    # send_msg.get_user_list()

    # title = '今天，为了这件大事，央视6位“名嘴”欢聚一堂！'
    # time = '2017-09-19 23:31:37'
    # content = '9月19日，2018年“CCTV国家品牌计划”发布会在京召开。本场发布会受到了社会各界的广泛关注...'
    # url = 'http://mp.weixin.qq.com/s?__biz=MTI0MDU3NDYwMQ==&mid=2656610975&idx=1&sn=e22e85b24d1ccbf0e55bfd810af49d7a&scene=0#wechat_redirect'
    # users = 'Liubo'
    # send_msg.send_msg(users, title, time, content, url)
    print(len('9月19日，2018年“CCTV国家品牌计划”发布会在京召开。本场发布会受到了社会各界的广泛关注...'))