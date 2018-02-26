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
from service.wechat_service import WechatService

class WechatAction():
    def __init__(self):
        corpid = 'wwd1c26293d0353651'
        send_msg_secret = 'e4nN9A5MN9yM1JY77-2oTk1i3H_2SWAw1saZ2X0ItuQ'
        sync_user_sercet = '2hd69k-1VcKRvwT5sWc7zgjObylVy-bstSUGo9lhh1c'
        agentid = 1000002
        self._wechat = WechatService(corpid, send_msg_secret, sync_user_sercet, agentid)

    def deal_request(self, name):
        web.header('Content-Type','text/html;charset=UTF-8')

        data = json.loads(json.dumps(web.input()))
        print(data)

        result = {"errcode":1,"errmsg":"地址错误","invaliduser":""}

        if name == 'get_user_list':
            result = self._wechat.get_user_list()

        elif name == 'send_msg':
            title = data.get('title')
            time = data.get('time')
            content = data.get('content')
            url = data.get('url')
            users = data.get('users')
            result = self._wechat.send_msg(users, title, time, content, url)

        elif name == 'send_file':
            users = data.get('users')
            file_path = data.get('file_path')
            media_id = self._wechat.upload_file(file_path)
            if media_id:
                result = self._wechat.send_file(users, media_id)
            else:
                result = {"errcode":1,"errmsg":"上传文件错误","invaliduser":""}

        elif name == 'add_user':
            user_name = data.get('name')
            mobile = data.get('mobile', '')
            email = data.get('email', '')
            user_id = data.get('user_id', '')
            enable = data.get('enable', 1)

            result = self._wechat.add_user(user_name, mobile, email, user_id, enable)

        elif name == 'update_user':
            user_name = data.get('name')
            mobile = data.get('mobile', '')
            email = data.get('email', '')
            user_id = data.get('user_id', '')
            enable = data.get('enable', 1)

            result = self._wechat.update_user(user_id, user_name, mobile, email, enable)

        elif name == 'del_user':
            user_id = data.get('user_id')
            result = self._wechat.del_user(user_id)

        # print(json.dumps(result))

        return "successCallback("+json.dumps(result)+")"

    def GET(self, name):
        return self.deal_request(name)

    def POST(self, name):
        return self.deal_request(name)

