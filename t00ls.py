#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import re
import time
import hashlib
import logging
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s')
                    # logging.basicConfig函数对日志的输出格式及方式做相关配置
# 由于日志基本配置中级别设置为DEBUG，所以一下打印信息将会全部显示在控制台上
# logging.info('this is a loggging info message')
# logging.debug('this is a loggging debug message')
# logging.warning('this is loggging a warning message')
# logging.error('this is an loggging error message')
# logging.critical('this is a loggging critical message')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
}

url_login = 'https://www.t00ls.net/login.html'
url_checklogin = 'https://www.t00ls.net/checklogin.html'
url_signin = 'https://www.t00ls.net/ajax-sign.json'

# questionid
# 1 母亲的名字
# 2 爷爷的名字
# 3 父亲出生的城市
# 4 您其中一位老师的名字
# 5 您个人计算机的型号
# 6 您最喜欢的餐馆名称
# 7 驾驶执照的最后四位数字

username = os.environ['USERNAME']          # 用户名
password = os.environ['PASSWORD']          # 明文密码或密码MD5
password_hash = False                      # 密码为md5时设置为True
questionid = os.environ['QUESTION']        # 问题ID，参考上面注释
answer = os.environ['ANSWER']              # 问题答案


def get_formhash(req):
    res = req.get(url=url_login, headers=headers, timeout=15)
    formhash_1 = re.findall('value="[0-9a-f]{8}"', res.content.decode("utf-8"))
    formhash = re.findall('[0-9a-f]{8}', formhash_1[0])[0]
    time.sleep(1)
    return formhash

def get_current_user(res):
    current_user = re.findall('<a href="members-profile-[\d+].*\.html" target="_blank">{username}</a>'.format(username=username), res.decode("utf-8"))
    cuser = re.findall('[\d+]{4,5}', ''.join(current_user))[0]
    return cuser

def login_t00ls(req):
    formhash = get_formhash(req)
    passwords = password if password_hash else hashlib.md5(password.encode("utf8")).hexdigest()
    data = {
        'username': username,
        'password': passwords,
        'questionid': questionid,
        'answer': answer,
        'formhash': formhash,
        'loginsubmit': '登录',
        'redirect': 'https://www.t00ls.net',
        'cookietime': '2592000'
    }
    headers['Referer'] = 'https://www.t00ls.net/'
    res = req.post(url=url_login, headers=headers, data=data, timeout=15)
    time.sleep(1)
    return res, formhash

def get_formhash_1(req):
    res = req.get(url=url_checklogin, headers=headers, timeout=15)
    uid = get_current_user(res.content)
    formhash = re.findall('[0-9a-f]{8}', res.content.decode("utf-8"))[0]
    return formhash, uid

def signin_t00ls(req):
    formhash, uid = get_formhash_1(req)
    data = {
        'formhash': formhash,
        'signsubmit': 'apply'
    }
    headers['Referer'] = 'https://www.t00ls.net/members-profile-{uid}.html'.format(uid=uid)
    res = req.post(url=url_signin, data=data, headers=headers, timeout=15)
    return res

if '__main__' == __name__:
    req = requests.session()
    res_login, formhash = login_t00ls(req)
    res_signin = signin_t00ls(req)
    logging.warning(res_signin.json())
