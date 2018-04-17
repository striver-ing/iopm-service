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
import init

from utils.log import log
import utils.tools as tools

HEADER = {
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

ORGANIZATION = tools.get_conf_value('config.conf', 'wechat', 'organization')

class WechatService():
    _depertment_id =  None

    def __init__(self, corpid, send_msg_secret, sync_user_sercet, agentid):
        self._agentid = agentid
        self._send_msg_access_token = self.get_access_token(corpid, send_msg_secret)
        self._sync_user_access_token = self.get_access_token(corpid, sync_user_sercet)

        if not WechatService._depertment_id:
            WechatService._depertment_id = self.get_depertment_id(ORGANIZATION)
            if not WechatService._depertment_id: # 通讯录中无此部门，新创建
                WechatService._depertment_id = self.add_department(ORGANIZATION)

    def get_access_token(self, corpid, secret):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s'%(corpid, secret)
        result = tools.get_json_by_requests(url, headers = HEADER)
        return result.get('access_token')

    def send_msg(self, users, title, time, content, article_url):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s'%self._send_msg_access_token
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
        result = tools.get_json_by_requests(url = url, headers = HEADER, data = data )
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
        url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s'%(self._send_msg_access_token, file_type)
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
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s'%self._send_msg_access_token
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
        result = tools.get_json_by_requests(url = url, headers = HEADER, data = data )
        return result

    def add_department(self, name):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token=%s'%self._sync_user_access_token
        data = {
           "name": name,
           "parentid": 1,
        }

        data = tools.dumps_json(data).encode('utf-8')
        result = tools.get_json_by_requests(url, headers = HEADER, data = data) # {'errcode': 0, 'id': 4, 'errmsg': 'created'}
        return result.get("id")

    def get_all_depertment(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token='+self._send_msg_access_token
        result = tools.get_json_by_requests(url)
        return result

    def get_depertment_id(self, name):
        departments = self.get_all_depertment().get('department')
        for department in departments:
            if department.get('name') == name:
                return department.get('id')

        return None

    def get_tags(self):
        '''
        @summary:
        ---------
        ---------
        @result:
        '''
        url = 'https://qyapi.weixin.qq.com/cgi-bin/tag/list?access_token='+self._send_msg_access_token
        result = tools.get_json_by_requests(url)
        tools.print(result)

    def __invite_user(self, user_id):
        '''
        @summary: 邀请成员
        ---------
        @param user_id:
        ---------
        @result:
        '''

        url = 'https://qyapi.weixin.qq.com/cgi-bin/batch/invite?access_token=' + self._sync_user_access_token
        data = {
           "user" : [user_id],
        }

        data = tools.dumps_json(data).encode('utf-8')
        result = tools.get_json_by_requests(url, headers = HEADER, data = data)
        return result


    def add_user(self, user_name, mobile, email = '', user_id = '', enable = 1):
        '''
        @summary: 添加用户
        access_token 中的secret 需使用管理工具中的通讯录同步的secret
        ---------
        @param user_name:
        @param mobile:
        @param email:
        @param user_id:
        @param enable: 启用成员 0 禁用 1 启用
        ---------
        @result:
        '''
        user_id = user_id if user_id else tools.get_uuid()

        # 返回的数据格式
        return_json = {
           "errcode": 0,
           "errmsg": "created",
           'user_id': user_id
        }


        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/create?access_token=' + self._sync_user_access_token
        data = {
           "userid": user_id,
           "name": user_name,
           "mobile": mobile,
           "department": [WechatService._depertment_id],
           "email": email,
           'enable':enable,
           'to_invite':False #是否邀请该成员使用企业微信（将通过微信服务通知或短信或邮件下发邀请，每天自动下发一次，最多持续3个工作日），默认值为true。
        }

        data = tools.dumps_json(data).encode('utf-8')
        result = tools.get_json_by_requests(url, headers = HEADER, data = data)

        if result.get('errcode') == 0:
            result = self.__invite_user(user_id)

        if result.get('errcode'):
            return_json['errcode'] = result.get('errcode')
            return_json['errmsg'] = result.get('errmsg')

        return return_json

    def get_user(self, user_id):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=%s&userid=%s'%(self._send_msg_access_token, user_id)
        result = tools.get_json_by_requests(url)
        return result

    def get_user_list(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=%s&department_id=%s&fetch_child=1'%(self._send_msg_access_token, WechatService._depertment_id)
        result = tools.get_json_by_requests(url)
        # tools.print(result)
        return result

    def update_user(self, user_id, user_name = '', mobile = '', email = '', enable = 1):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/update?access_token=' + self._sync_user_access_token
        data = {
           "userid": user_id,
           "name": user_name,
           "mobile": mobile,
           "email": email,
           "enable": 1,
        }

        data = tools.dumps_json(data).encode('utf-8')
        result = tools.get_json_by_requests(url, headers = HEADER, data = data)
        return result

    def del_user(self, user_id):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/delete?access_token=%s&userid=%s'%(self._sync_user_access_token, user_id)
        result = tools.get_json_by_requests(url, headers = HEADER)
        return result

if __name__ == '__main__':
    corpid = 'wwd1c26293d0353651'
    send_msg_secret = 'e4nN9A5MN9yM1JY77-2oTk1i3H_2SWAw1saZ2X0ItuQ'
    sync_user_sercet = '2hd69k-1VcKRvwT5sWc7zgjObylVy-bstSUGo9lhh1c'
    agentid = 1000002
    wechat = WechatService(corpid, send_msg_secret, sync_user_sercet, agentid)

    result = wechat.add_user("王五", "15566264007" )
    print(result)
