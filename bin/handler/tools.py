# -*- coding: utf-8 -*-
import sys
import json
import inspect
import logging
import datetime
from zbase.base.dbpool import get_connection_exception
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

def gen_offset(page, maxnum):
     limit = maxnum
     offset = (page -1) * maxnum
     return offset, limit


def get_current_func():
    return sys._getframe().f_code.co_name


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
        values = {'name': name, 'item_type': item_type, 'content': content}
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


def prescription_add_item(prescription_id, userid, item_id, count, train_type,  param):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        values = {
            'presc_id': prescription_id,
            'userid': userid,
            'item_id': item_id,
            'count': count,
            'train_type': train_type,
            'params': param,
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


def prescription_update_item(presc_id, presc_item_id, count, train_type, param_str):
    with get_connection_exception('uyu_core') as conn:
        now = datetime.datetime.now()
        where = {'presc_id': presc_id, 'id': presc_item_id}
        values = {'count': count, 'train_type': train_type, 'params': param_str, 'utime': now}
        ret = conn.update(table='presc_items', values=values, where=where)
        log.debug('func=%s|db ret=%d', inspect.stack()[0][3], ret)
        if ret == 1:
            return True
        return False

