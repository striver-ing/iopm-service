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
import web
import json
from service.send_msg_to_wechat_service import SendMsgToWechatService

class SendMsgToWechatAction():
    def __init__(self):
        corpid = 'wwd1c26293d0353651'
        secret = 'e4nN9A5MN9yM1JY77-2oTk1i3H_2SWAw1saZ2X0ItuQ'
        agentid = 1000002
        self._wechat = SendMsgToWechatService(corpid, secret, agentid)

    def deal_request(self, name):
        web.header('Content-Type','text/html;charset=UTF-8')

        data = json.loads(json.dumps(web.input()))
        print(data)

        result = {"errcode":1,"errmsg":"地址错误","invaliduser":""}

        if name == 'get_user_list':
            print('get_user_list')
            result = self._wechat.get_user_list()

        elif name == 'send_msg':
            title = data.get('title')
            time = data.get('time')
            content = data.get('content')
            url = data.get('url')
            users = data.get('users')
            result = self._wechat.send_msg(users, title, time, content, url)

        # print(json.dumps(result))

        return "successCallback("+json.dumps(result)+")"

    def GET(self, name):
        return self.deal_request(name)

    def POST(self, name):
        return self.deal_request(name)

