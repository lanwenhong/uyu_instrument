# -*- coding: utf-8 -*-
import os
import sys
import json
import redis
import qrcode
import base64
import StringIO
import inspect
import logging
import datetime
import hashids
import config
from PIL import Image
from zbase.base.dbpool import get_connection_exception
from zbase.base.http_client import RequestsClient
from zbase.server.client import HttpClient
from uyubase.uyu import define
log = logging.getLogger()

PARAMS_KEY_INT = [
    'trade_type', 'eye_type', 'font_size',
    'line_count', 'pic_count', 'line_type',
]

PARAMS_KEY_STR = ['left_eye_level', 'right_eye_level']

PARAMS_KEY = PARAMS_KEY_INT + PARAMS_KEY_STR

PARAM_TRADE_TYPE_MAP = {
    '0': u'无',
    '1': u'集合',
    '2': u'散开'
}

PARAM_EYE_TYPE_MAP = {
    '0': '无',
    '1': '单眼',
    '2': '双眼'
}

CHECK_ITEM_NAME = {
    '视力检查': {
        'keys': {
            'seq': {
                'must': ['optic', 'font_size', 'vision', 'eye'],
                'option': []
            },
            'glasses': True
        }
    },
    '红绿检查': {
        'keys': {
            'seq': {
                'must': ['eye', 'color'],
                'option': []
            },
            'glasses': True
        }
    },
    'worth4点': {
        'keys': {
            'seq': {
                'must': ['optic', 'pic_num'],
                'option': ['pic_pos']
            }
        }
    },
    '眼位测量': {
        'keys': {
            'seq': {
                'must': ['optic', 'overlap_dis1', 'overlap_dis2'],
                'option': []
            }
        },
        'func': 'eye_level_measurement'
    },
    '眼位测量2': {
        'keys': {
            'seq': {
                'must': ['optic', 'pos'],
                'option': []
            }
        }
    },
    '融像检查': {
        'keys': {
            'seq': {
                'must': ['optic', 'pic_dis_blur', 'pic_dis_burst', 'pic_dis_recover', 'base'],
                'option': []
            }
        }
    },
    '调节功能检查': {
        'keys': {
            'seq': {
                'must': ['adjust', 'eye', 'optic', 'pad_dis'],
                'option': ['excite']
            }
        },
        'func': 'calc_excite'
    },
    '调节灵敏度': {
        'keys': {
            'seq': {
                'must': ['eye', 'cycle', 'press_time'],
                'option': []
            }
        }
    },
    '聚散灵敏度': {
        'keys': {
            'seq': {
                'must': ['cycle', 'press_time'],
                'option': []
            }
        }
    },
    '色觉检查': {
        'keys': {
            'seq': {
                'must': ['color', 'color_sense'],
                'option': []
            }
        }
    },
    '立体视检查': {
        'keys': {
            'seq': {
                'must': ['pic_name'],
                'option': []
            }
        }
    }
}

def check_result(name, result):
    flag = True
    check = CHECK_ITEM_NAME.get(name)['keys']
    if 'glasses' in check.keys():
        if result['glasses'] not in (True, False):
            log.warn('func=%s|key=%s|vlaue=%s|invalid', 'check_result', 'glasses', result['glasses'])
            return False
    if not isinstance(result, dict):
        log.warn('func=%s|result=%s|type eror', 'check_result', result)
        return False
    if 'seq' not in result.keys():
        log.warn('func=%s|seq not exists', 'check_result')
        return False
    seq = result['seq']
    if not isinstance(seq, list):
        log.warn('func=%s|key=%s|invalid', 'check_result', 'seq')
        return False
    must_keyes = check['seq']['must']
    for item in seq:
        for key in must_keyes:
            if not item.has_key(key):
                log.warn('func=%s|key=%s|not exist', 'check_result', key)
                flag = False
                return flag
            if key == 'press_time':
                # 检查类型是list
                value = item[key]
                if not isinstance(value, list):
                    log.warn('func=%s|key=%s|value type error', 'check_result', key)
                    flag = False
                    return flag
                # 是一个list检查每一项的类型
                for v in value:
                    if not isinstance(int(v), int):
                        log.warn('func=%s|key=%s|v error', 'check_result', key)
                        flag = False
                        return flag

    f_n = CHECK_ITEM_NAME.get(name).get('func', None)
    if f_n:
        func_map = globals()
        func = func_map.get(f_n)
        if callable(func):
            func(result)
    return flag


def gen_offset(page, maxnum):
    limit = maxnum
    offset = (page -1) * maxnum
    return offset, limit


def get_current_func():
    return sys._getframe().f_code.co_name


def verify_item_type(item_type):
    log.debug('func=%s|item_type=%s|type=%s', inspect.stack()[0][3], item_type, type(item_type))
    flag = True
    if int(item_type) not in (define.UYU_ITEM_CHECK, define.UYU_ITEM_TRAIN):
        flag = False
    log.debug('func=%s|ret=%s', inspect.stack()[0][3], flag)
    return flag


def verify_trade_type(trade_type):
    if str(trade_type) in PARAM_TRADE_TYPE_MAP.keys():
        return True
    return False


def verify_eye_type(eye_type):
    if str(eye_type) in PARAM_EYE_TYPE_MAP.keys():
        return True
    return False


def verify_user(userid, user_type=None):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': userid}
        if user_type is not None:
            where['user_type'] = user_type
        ret = conn.select_one(table='auth_user', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def verify_train_user(userid):
    with get_connection_exception('uyu_core') as conn:
        where = {
            'id': userid,
            'user_type': ('in', [define.UYU_USER_ROLE_COMSUMER, define.UYU_USER_ROLE_EYESIGHT])
        }
        ret = conn.select_one(table='auth_user', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def verify_device_info(device_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': device_id}
        ret = conn.select_one(table='device', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def verify_presc(prescription_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': prescription_id}
        ret = conn.select_one(table='prescription', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def verify_item(item_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': item_id}
        ret = conn.select_one(table='item', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def check_item_by_name(name):
    log.debug('func=%s|name=%s', inspect.stack()[0][3], name)
    with get_connection_exception('uyu_core') as conn:
        where = {'name': name}
        ret = conn.select_one(table='item', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def verify_param(param):
    flag = True
    print 'verify_param input:', param
    for key in PARAMS_KEY:
        if key in PARAMS_KEY_STR:
            value = param.get(key, None)
            log.info('verify_param key=%s|value=%s|type=%s', key, value, type(value))
            if value is not None:
                if not isinstance(value, basestring):
                    flag = False
                    break

        if key in PARAMS_KEY_INT:
            value = param.get(key, None)
            log.info('verify_param key=%s|value=%s|type=%s', key, value, type(value))
            if value is not None:
                if not isinstance(value, int):
                    flag = False
                    break
                if key == 'trade_type':
                    ret  = verify_trade_type(value)
                    if not ret:
                        flag = ret
                        break
                if key == 'eye_type':
                    ret = verify_eye_type(value)
                    if not ret:
                        flag = ret
                        break
    log.debug('func=%s|return=%s|key=%s', inspect.stack()[0][3], flag, key)
    return flag


def verify_presc_item(presc_item_id):
    with get_connection_exception('uyu_core') as conn:
        ret = conn.select_one(table='presc_items', fields='*', where={'id': presc_item_id})
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def verify_train(train_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': train_id}
        ret = conn.select_one(table='train', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def get_channel_info(channel_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': channel_id}
        ret = conn.select_one(table='channel', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def get_store_info(store_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': store_id}
        ret = conn.select_one(table='stores', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def get_user_presc(userid):
    with get_connection_exception('uyu_core') as conn:
        where = {'userid': userid}
        ret = conn.select_one(table='prescription', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def get_all_presc_item(presc_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'presc_id': presc_id}
        ret = conn.select(table='presc_items', fields='*', where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def get_presc_item_content(presc_id):
    content = []
    items = get_all_presc_item(presc_id)
    with get_connection_exception('uyu_core') as conn:
        for item in items:
            item_id = item['item_id']
            ret = conn.select_one(table='item', fields=['content'], where={'id': item_id})
            content.append(ret['content'])
        return content


def get_train_result(train_id):
    log.debug('func=%s|train_id=%s', inspect.stack()[0][3], train_id)
    with get_connection_exception('uyu_core') as conn:
        where = {'train_id': train_id}
        ret = conn.select(table='result', fields=['result', 'item_name'], where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def get_store_info(store_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': store_id}
        ret = conn.select_one(table='stores', fields='*', where=where)
        return ret


def item_create(name, item_type, content):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        values = {
            'name': name,
            'item_type': item_type,
            'content': content,
            'ctime': now,
            'utime': now
        }
        ret = conn.insert(table='item', values=values)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            item_id = conn.last_insert_id()
            return item_id
        return None


def item_update(name, item_type, content, item_id):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        where = {'id': item_id}
        values = {'name': name, 'item_type': item_type, 'content': content, 'utime': now}
        ret = conn.update(table='item', values=values, where=where)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            return True
        return False


def item_info(item_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': item_id}
        keep_fields = ['id', 'name', 'item_type', 'content', 'state']
        ret = conn.select_one(table='item', fields=keep_fields, where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def item_list(offset, limit):
    with get_connection_exception('uyu_core') as conn:
        other = ' order by ctime desc limit %d offset %d' % (limit, offset)
        keep_fields = ['id', 'name', 'item_type', 'content', 'state']
        ret = conn.select(table='item', fields=keep_fields, other=other)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return ret


def item_total():
    with get_connection_exception('uyu_core') as conn:
        sql = 'select count(*) as total from item where ctime>0'
        ret = conn.get(sql)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return int(ret['total']) if ret['total'] else 0


def prescription_create(userid, optometrist_id):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        values = {
            'userid': userid, 'optometrist_id': optometrist_id,
            'ctime': now, 'utime': now
        }
        ret = conn.insert(table='prescription', values=values)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            prescription_id = conn.last_insert_id()
            return prescription_id
        else:
            return None


def prescription_update(prescription_id, userid, optometrist_id):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        values = {
            'userid': userid,
            'optometrist_id': optometrist_id,
            'utime': now
        }
        where = {'id': prescription_id}
        ret = conn.update(table='prescription', values=values, where=where)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            return True
        return False


def prescription_info(prescription_id):
    with get_connection_exception('uyu_core') as conn:
        where = {'id': prescription_id}
        keep_fields = ['id', 'userid', 'optometrist_id']
        presc_info = conn.select_one(table='prescription', fields=keep_fields, where=where)
        presc_item_keep_fields = ['id', 'item_id', 'count', 'params']
        items = conn.select(table='presc_items', fields=presc_item_keep_fields, where={'presc_id': prescription_id})
        return presc_info, items


def prescription_add_item(prescription_id, userid, item_id, count, param_str):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        values = {
            'presc_id': prescription_id,
            'userid': userid,
            'item_id': item_id,
            'count': count,
            'params': param_str,
            'ctime': now,
            'utime': now,
        }
        ret = conn.insert(table='presc_items', values=values)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret != 1:
            return None

        presc_item_id = conn.last_insert_id()
        return presc_item_id


def prescription_del_item(presc_id, presc_item_id):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        where = {'presc_id': presc_id, 'id': presc_item_id}
        values = {'is_valid': define.UYU_PRESC_ITEM_UNBIND, 'utime': now}
        ret = conn.update(table='presc_items', values=values, where=where)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            return True
        return False


def prescription_update_item(presc_id, presc_item_id, count):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        where = {'presc_id': presc_id, 'id': presc_item_id}
        values = {'count': count, 'utime': now}
        ret = conn.update(table='presc_items', values=values, where=where)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            return True
        return False


def train_create(param, channel_id, store_id, presc_id):
    channel_userid = get_channel_info(channel_id).get('userid')
    store_userid = get_store_info(store_id).get('userid')
    content = get_presc_item_content(presc_id)
    now = datetime.datetime.now()
    with get_connection_exception('uyu_core') as conn:
        param['channel_id'] = channel_userid
        param['store_id'] = store_userid
        param['presc_id'] = presc_id
        param['state'] = define.UYU_TRAIN_STATE_START
        param['step'] = 0
        param['times'] = 0
        param['presc_content'] = json.dumps(content)
        param['ctime'] = now
        param['utime'] = now
        ret = conn.insert(table='train', values=param)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            train_id = conn.last_insert_id()
            return train_id
        return None


def train_info(train_id):
    result = get_train_result(train_id)
    with get_connection_exception('uyu_core') as conn:
        where = {'id': train_id}
        keep_fields = [
            'id', 'userid', 'channel_id', 'store_id',
            'device_id', 'presc_content', 'item_type',
            'state', 'step', 'lng', 'lat', 'times',
            'ctime', 'utime'
        ]
        ret = conn.select_one(table='train', fields=keep_fields, where=where)
        if not ret:
            return None
        else:
            if ret['lng']:
                ret['lng'] = float(ret['lng'])
            else:
                ret['lng'] = 0.00

            if ret['lat']:
                ret['lat'] = float(ret['lat'])
            else:
                ret['lat'] = 0.00
                
        if not result:
            ret['result'] = []
            return ret
        # ret['result'] = [item['result'] for item in result]
        ret['result'] = [{'name': item['item_name'], 'result': item['result']} for item in result]
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        if ret:
            ret['ctime'] = datetime.datetime.strftime(ret['ctime'], '%Y-%m=%d %H:%M:%S')
            if ret['utime']:
                ret['utime'] = datetime.datetime.strftime(ret['utime'], '%Y-%m=%d %H:%M:%S')


        return ret


def train_list(offset, limit, userid=''):
    with get_connection_exception('uyu_core') as conn:
        where = {}
        if userid not in ('', None):
            where['userid'] = userid
        other = ' order by ctime desc limit %d offset %d' % (limit, offset)
        ret = conn.select(table='train', fields='*', where=where, other=other)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        if ret:
            for item in ret:
                result = get_train_result(item['id'])
                if result:
                    # item['result'] = [r['result'] for r in result]
                    item['result'] = [{'name': r['item_name'], 'result': r['result']} for r in result]
                else:
                    item['result'] = []
                item['ctime'] = datetime.datetime.strftime(item['ctime'], '%Y-%m=%d %H:%M:%S')
                if item['utime']:
                    item['utime'] = datetime.datetime.strftime(item['utime'], '%Y-%m=%d %H:%M:%S')
                if item['lng']:
                    item['lng'] = float(item['lng'])
                else:
                    item['lng'] = 0.00
                if item['lat']:
                    item['lat'] = float(item['lat'])
                else:
                    item['lat'] = 0.00

        return ret


def train_total(userid=''):
    with get_connection_exception('uyu_core') as conn:
        where = {'ctime': ('>', 0)}
        if userid not in ('', None):
            where['userid'] = userid
        # sql = 'select count(*) as total from train where ctime>0'
        # ret = conn.get(sql)
        ret = conn.select(table='train', fields='count(*) as total', where=where) 
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        return int(ret[0]['total']) if ret[0]['total'] else 0


def train_complete(train_id, step, result, name, presc_id, item_id, isend, times=''):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        where = {'id': train_id}
        values = {
            'step': step,
            # 'state': define.UYU_TRAIN_STATE_END,
            'state': int(isend),
            'utime': now
        }
        if times:
            values['times'] = times
        ret = conn.update(table='train', values=values, where=where)
        log.debug('func=%s|update train|ret=%s', inspect.stack()[0][3], ret)
        if ret != 1:
            return False
        ret = conn.select_one(table='result', fields='*', where={
            'train_id': train_id, 
            'presc_id': presc_id,
            'item_id': item_id
        })
        if ret:
            ret = conn.update(
                table='result', 
                values={'result': json.dumps(result), 'utime': now},
                where={'id': ret['id']}
            )
            log.debug('func=%s|update result|ret=%s', inspect.stack()[0][3], ret)
            if ret != 1:
                return False
        else:
            ret = conn.insert(table='result', values={
                'train_id': train_id,
                'presc_id': presc_id,
                'item_id': item_id,
                'item_name': name,
                'result': json.dumps(result),
                'ctime': now,
                'utime': now
            })
            log.debug('func=%s|insert result|ret=%s', inspect.stack()[0][3], ret)
            if ret != 1:
                return False
        return True


def train_close(train_id):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        where = {'id': train_id}
        values = {
            'state': define.UYU_TRAIN_STATE_CLOSE,
            'utime': now
        }
        ret = conn.update(table='train', values=values, where=where)
        log.debug('func=%s|db ret=%s', inspect.stack()[0][3], ret)
        if ret == 1:
            return True
        return False


def gen_qrcode_base64(qrcode_txt):
    qr = qrcode.QRCode()
    qr.add_data(qrcode_txt)
    img = qr.make_image()
    f = StringIO.StringIO()
    img.save(f)
    d = base64.b64encode(f.getvalue())
    f.close()
    ret = 'data:image/png;base64,' + d
    return ret


def gen_qrcode_file(qrcode_txt):
    log.debug('func=%s|qrcode_txt=%s', inspect.stack()[0][3], qrcode_txt)
    flag = True
    now = datetime.datetime.now()
    filename = now.strftime('%Y%m%d%H%M%S%f') + '.png'
    full_name = config.QRCODE_STORE_PATH + filename 
    qr = qrcode.QRCode()
    qr.add_data(config.QRCODE_CONTENT_PREFIX+qrcode_txt)
    img = qr.make_image()
    out = img.resize(config.IMAGE_SIZE, Image.ANTIALIAS)
    region = out.crop(config.IMAGE_BOX)
    region.save(full_name)
    if not os.path.exists(full_name):
        flag = False
    log.debug('func=%s|ret|flag=%s|filename=%s', inspect.stack()[0][3], flag, filename)
    return flag, filename


def call_api_change(userid, store_userid, training_times, device_id, train_id):
    flag = True
    record_id = None
    data = {
        'userid': userid,
        'store_userid': store_userid,
        'training_times': training_times,
        'device_id': device_id,
        'train_id': train_id
    }
    url = config.API_SERVER['url']
    port = config.API_SERVER['port']
    host = config.API_SERVER['host']
    timeout = config.API_SERVER['timeout']
    server = [{'addr': (host, port), 'timeout': timeout}]
    client = HttpClient(server, client_class=RequestsClient)
    ret = client.post(url, data)
    log.debug('func=%s|post ret=%s', inspect.stack()[0][3], ret)
    result = json.loads(ret)
    respcd = result.get('respcd')
    if respcd != '0000':
        flag = False
    else:
        record_id = result['data']['record_id']
    log.debug('func=%s|ret|flag=%s|record_id=%s', inspect.stack()[0][3], flag, record_id)
    return flag, record_id


def eye_level_measurement(data):
    # 暂时返回一个固定的
    finish = [
        {"optic":250, "overlap_dis": 1},
        {"optic":0, "overlap_dis": 2}
    ]
    data["result"] = finish
    log.debug('func=%s|ret=%s', inspect.stack()[0][3], data)
    return data


def calc_excite(data):
    # 暂时返回一个固定的
    for item in data['seq']:
        item['excite'] = 1
    log.debug('func=%s|ret=%s', inspect.stack()[0][3], data)
    return data


def push_msg(token, data):
    try:
        data = {'token': token, 'msg': json.dumps(data)}
        url = config.PUSH_SERVER['url']
        port = config.PUSH_SERVER['port']
        host = config.PUSH_SERVER['host']
        timeout = config.PUSH_SERVER['timeout']
        server = [{'addr': (host, port), 'timeout': timeout}]
        client = HttpClient(server, client_class=RequestsClient)
        ret = client.post(url, data)
        log.debug('func=%s|post ret=%s', inspect.stack()[0][3], ret)
    except Exception as e:
        log.warn(e)
        log.warn(traceback.format_exc())


def update_train(train_id, record_id):
    log.debug('func=%s|in|train_id=%s|record_id=%s', inspect.stack()[0][3], train_id, record_id)
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        values = {'record_id': record_id, 'utime': now}
        where = {'id': train_id}
        ret = conn.update(table='train', values=values, where=where)
        log.debug('func=%s|update ret=%s', inspect.stack()[0][3], ret)
        return ret

def gen_device_key(device_id):
    h = hashids.Hashids('~~~uyu~~~')
    key = h.encode(device_id)
    return key


def check_device_token(redis_pool, device_id):
    log.debug('func=%s|in|device_id=%s', inspect.stack()[0][3], device_id)
    result = None
    client = redis.StrictRedis(connection_pool=redis_pool)
    device_prefix_key = 'uyu_device_%s' % device_id
    v = client.get(device_prefix_key)
    log.debug('device_prefix_key=%s|value=%s', device_prefix_key, v)
    if v:
        result = v
    log.debug('func=%s|out|result=%s', inspect.stack()[0][3], result)
    return result
