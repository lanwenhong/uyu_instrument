# -*- coding: utf-8 -*-
import os
HOME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bin')
rtenv = 'product'

LOGFILE = {
    'root': {
        'filename': {
            'DEBUG': os.path.join(HOME, '../log/instrument.log'),
            'ERROR': os.path.join(HOME, '../log/instrument.error.log'),
        }
    }
}

database = {
    'uyu_core':{
        'engine': 'pymysql',
        'passwd': '123456',
        'charset': 'utf8',
        'db': 'ychannel',
        'idle_timeout': 10,
        'host': '127.0.0.1',
        'user': 'yyy',
        'port': 3306,
        'conn': 3
    }
}

# web config
# URLS配置
URLS = None
# 静态路径配置
STATICS = {'/static/':'/static/'}
# 模板配置
TEMPLATE = {
    'cache': True,
    'path': '',
    'tmp': os.path.join(HOME, '../tmp'),
}
# 中间件
MIDDLEWARE = ()
# WEB根路径
DOCUMENT_ROOT = HOME
# 页面编码
CHARSET = 'UTF-8'
# APP就是一个子目录
APPS = ()
DATABASE = {}
# 调试模式: True/False
# 生产环境必须为False
DEBUG = True
# 模版路径
template = os.path.join(HOME, 'template')

# 服务地址
HOST = '0.0.0.0'
# 服务端口
PORT = 8088
#redis
redis_url = 'redis://127.0.0.1:4600/0'
#cookie 配置
cookie_conf = { 'expires':60*60*24*3, 'max_age':60*60*24*3, 'domain':'121.40.177.111', 'path':'/instrument'}
API_SERVER = {
    'url': '/internal/v1/api/consumer_change',
    'port': 8087,
    'host': '127.0.0.1',
    'timeout': 2000
}
PUSH_SERVER = {
    'url': '/v1/msg/push',
    'port': 8090,
    'host': '127.0.0.1',
    'timeout': 2000
}
#二维码图片存放位置
QRCODE_STORE_PATH = '/home/dengcheng/uyu_instrument/tmp/'
QRCODE_LINK_BASE = 'http://121.40.177.111:10040/static/'
