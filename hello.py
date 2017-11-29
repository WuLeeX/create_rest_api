# !/usr/bin/python3

import requests
import json
import urllib
from http.server import BaseHTTPRequestHandler,HTTPServer
#--------------------------------
# 获取微信公众号token
#--------------------------------
'''
url = "https://api.weixin.qq.com/cgi-bin/token"
param = {
        "grant_type" : "client_credential",
        "AppID": "wx14a196fb52ca1870",
        "Secret": "e19bae8a7233c700138a95e9a4352474",
}
'''

class Basic:
    def __init__(self):
        self._accessToken = ''
        self._leftTime = 0

    def _real_get_access_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token"
        param = {
            "grant_type": "client_credential",
            "AppID": "wxb29a9d16a8e3636d",
            "Secret": "8540a9beb945430c5db2342e16e4060d"
        }

        url_resp = requests.post(url, params=param)
        if url_resp.status_code != requests.codes.ok:
            print("post error")
            return []
        data = url_resp.json()
        self._accessToken = data['access_token']
        self._leftTime = data['expires_in']

    def get_access_token(self):
        if self._leftTime < 10:
            self._real_get_access_token()

        return self._accessToken


class Customer_Service:
    def __init__(self):
        self._kf_account = ""
        self._nickname = ""
        self._password = ""

    def add_customer_service(self):
        '''
            添加客服账号
            http请求方式: POST
            https://api.weixin.qq.com/customservice/kfaccount/add?access_token=ACCESS_TOKEN
        '''
        url = "https://api.weixin.qq.com/customservice/kfaccount/add"
        data = {
            "kf_account" : "test1@test",
            "nickname" : "customservice1",
            "password" : "pswmd1"
        }

        url_resp = requests.post(url, data = data, params = { "access_token" : Basic().get_access_token() })
        response = url_resp.json()
        if response['errcode'] != 0:
            print("add customer service error")
            return "test1"
        else:
            print("add customer service %s success!" %(data['kf_account']))
            return data['kf_account']

    def send_cs_msg(self, kfaccount):
        '''
            http请求方式: POST
            https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=ACCESS_TOKEN
        '''
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send"
        data = {
                "touser" : "ouG3W0T_hmRKhyco_7B4bCqb5ShM",
                "msgtype" : "text",
                "text" : AlarmHandler.do_POST(),
                "customservice":
                {
                    "kf_account" : kfaccount
                }
        }
        url_resp = requests.post(url, data=data, params={"access_token": Basic().get_access_token()})
        response = url_resp.json()
        if response['errcode'] != 0:
            print("send customer service message error, msg = %s" %(data['text']))
#            pprint(json.loads(data['text']))
        else:
            print("add customer service message success! the message is %s." % (data['text']))

class TemplateMessage:
    '''实现模板发送告警信息'''
    '''
    模板消息调用时主要需要模板ID和模板中各参数的赋值内容。请注意：
    1.模板中参数内容必须以".DATA"结尾，否则视为保留字;
    2.模板保留符号"{{ }}"
    '''
    def set_industry(self):
        pass

    def get_template_id(self):
        template_id = 'UP3hahFEFuJjZvP5VDAnxxE5563UrPK_g7EWRhV4tfU'
        return template_id
"""
    def send_template_msg(self):
        ''' 发送模板消息：
            http请求方式: POST
            https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=ACCESS_TOKEN

            发送的格式如下：
        {
           "touser":"OPENID",
           "template_id":"ngqIpbwh8bUfcSsECmogfXcV14J0tQlEpBO27izEYtY",
           "url":"http://weixin.qq.com/download",  
           "miniprogram":{
             "appid":"xiaochengxuappid12345",
             "pagepath":"index?foo=bar"
           },          
           "data":{
                   "first": {
                       "value":"恭喜你购买成功！",
                       "color":"#173177"
                   },
                   "keynote1":{
                       "value":"巧克力",
                       "color":"#173177"
                   },
                   "keynote2": {
                       "value":"39.8元",
                       "color":"#173177"
                   },
                   "keynote3": {
                       "value":"2014年9月22日",
                       "color":"#173177"
                   },
                   "remark":{
                       "value":"欢迎再次购买！",
                       "color":"#173177"
                   }
           }
        }

        '''
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'
        print(url)

        basic = Basic()
        template = TemplateMessage()
        param = {'access_token' : basic.get_access_token()}
        send_data = {
            "touser": "ouG3W0T_hmRKhyco_7B4bCqb5ShM",
            "template_id": template.get_template_id(),
            "data": {
                "first": {
                    "value": "告警通知：",
                    "color": "#FF0000"
                },
                "state": {
                    "value": self.parse_data()[0]['status'],
                    "color": "#173177"
                },
                "annotation": {
                    "value": self.parse_data()[0]['annotations'],
                    "color": "#173177"
                },
                "labels": {
                    "value": self.parse_data()[0]['labels'],
                    "color": "#173177"
                },
                "time": {
                    "value": self.parse_data()[0]['startsAt'],
                    "color":"#173177"
                },
                "remark": {
                    "value": "详见Alertmanager！",
                    "color": "#173177"
                }
            }
        }
        req = requests.post(url, data=json.dumps(send_data), params = param)
        response = req.json()
        if response['errcode'] != 0:
            print('send msg failed!, errcode is: {0}, \
                  and errmsg is: {1}'.format(response['errcode'], response['errmsg']))
        else:
            print('OK')
"""

class AlarmHandler(BaseHTTPRequestHandler):
    '''获取alertmanager上的告警数据'''
    def do_POST(self):
        '''响应POST请求'''
        self.send_response(200, 'OK')
        self.send_header("Content-type", "text/html")
        self.send_header("test", "This is test!")
        self.end_headers()
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        # data 是个字典
        print(data)

        ''' 发送通知 '''
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'
        print(url)

        basic = Basic()
        template = TemplateMessage()
        if 'alerts' in data:
            param = {'access_token': basic.get_access_token()}
            send_data = {
                "touser": ["ouG3W0RkbNLvzKLNJnTCyJwzaxWs","ouG3W0T_hmRKhyco_7B4bCqb5ShM"],
                "template_id": template.get_template_id(),
                "data": {
                    "first": {
                        "value": "告警通知：",
                        "color": "#FF0000"
                    },
                    "state": {
                        "value": data['alerts'][0]['status'],
                        "color": "#173177"
                    },
                    "annotation": {
                        "value": json.dumps(data['alerts'][0]['annotations']['summary']),
                        "color": "#173177"
                    },
                    "labels": {
                        "value": json.dumps(data['alerts'][0]['labels']['instance']),
                        "color": "#173177"
                    },
                    "time": {
                        "value": data['alerts'][0]['startsAt'],
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "详见Alertmanager！",
                        "color": "#173177"
                    }
                }
            }
            req = requests.post(url, data=json.dumps(send_data), params=param)
            response = req.json()
            if response['errcode'] != 0:
                print('send msg failed!, errcode is: {0}, \
                              and errmsg is: {1}'.format(response['errcode'], response['errmsg']))
            else:
                print('OK')


        return data

    def parse_data(self):
        # data['alerts'] 是告警列表，包括以下信息：
        '''
        "annotations": {"description":"<string>", "summary":"<string>"}
        "endsAt": "<time string>"
        "generatorURL": "<URL_string>"
        "labels": "<several strings>"
        "startsAt": "<time string>"
        "status": "<firing | resolved>"
        '''
        status = ['annotations','labels','startsAt','status']
        data = self.do_POST()
        parse_result = {}
        if 'alerts' in data:
            length = len(data['alerts'])
            for i in length:
                for state in status:
                    parse_result[i][state] = data[i][state]

        return parse_result

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("test", "This is test!")
        self.end_headers()
        buf = ''' <!DOCTYPE HTML>
                  <html> 
                  <head><title>Get page</title></head>
                      <body>
                          <form action="post_page" method="post">
                              username: <input type="text" name="username" /><br />
                              password: <input type="text" name="password" /><br />
                              <input type="submit" value="POST" />
                          </form>
                      </body>
                  </html>'''
        self.wfile.write(buf.encode())


def main():

    httpd = HTTPServer(('', 1234), AlarmHandler)
    httpd.serve_forever()


"""
def get_alert():
    '''获取alertmanager上的告警数据'''
    url = 'http://10.110.13.216:9093/api/v1/alerts'
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        print("get alert failed!")
        return []
    else:
        data = response.json()
        return data['data']
"""

def get_user():
    '''获取用户信息'''
    pass

def send_message():
    '''将告警发送给用户'''
    pass

if __name__ == '__main__':
    main()

