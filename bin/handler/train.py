# -*- coding: utf-8 -*-
import math
import uuid
import json
import inspect
import traceback
from zbase.web import core
from zbase.web import template
from zbase.web.validator import with_validator_self, Field, T_REG, T_INT, T_STR, T_FLOAT
from zbase.base.dbpool import with_database
from uyubase.base.dsession import uyu_check_device_session
from uyubase.base.response import success, error, UAURET
from uyubase.uyu import define
from uyubase.base.uyu_device import UDevice
from uyubase.uyu.define import UYU_OP_ERR, UYU_OP_OK
import logging, datetime, time

from runtime import g_rt
from config import cookie_conf
import tools
log = logging.getLogger()


class CreateHandler(core.Handler):

    _post_handler_fields = [
        Field('userid', T_INT, False),
        Field('device_id', T_INT, False),
        # Field('record_id', T_INT, False),
        Field('item_type', T_INT, False, match=r'^([1-2]){1}$'),
        Field('lng', T_FLOAT, False),
        Field('lat', T_FLOAT, False),
        Field('token', T_STR, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        params.pop("token")
        userid = params.get('userid')
        device_id = params.get('device_id')
        item_type = params.get('item_type')
        lng = params.get('lng')
        lat = params.get('lat')
        flag = tools.verify_train_user(userid)
        if not flag:
            return error(UAURET.ROLEERR)
        ret = tools.verify_device_info(device_id)
        if not ret:
            log.warn('device invalid device_id=%s', device_id)
            return error(UAURET.DATAERR)
        blooth_tag = ret.get('blooth_tag')
        channel_id = ret.get('channel_id', None)
        store_id = ret.get('store_id', None)
        if store_id == None or channel_id == None:
            log.warn('device no bind device_id=%s|channel_id=%s|store_id=%s|', device_id, channel_id, store_id)
            return error(UAURET.DEVICEUNBINDERR)
        ret = tools.get_store_info(store_id)
        store_userid = ret['userid']
        ret = tools.get_user_presc(userid)
        if not ret:
            return error(UAURET.USERNOPRESCERR)
        presc_id = ret['id']
        train_id = tools.train_create(params, channel_id, store_id, presc_id)
        if train_id is None:
            return error(UAURET.DATAERR)
        params['id'] = train_id
        token = self.device.se.sk
        push_data = {"msgid": str(uuid.uuid4()), "data": {}}
        if item_type == define.UYU_ITEM_TYPE_TRAIN:
            push_data["type"] = "train"
            push_data["data"]["id"] = train_id
            flag = tools.call_api_change(userid, store_userid, 1, device_id, train_id)
            if not flag:
                return error(UAURET.SUBTIMESERR)
        else:
            push_data["type"] = "inspect"
            push_data["data"]["id"] = train_id
        tools.push_msg(token, push_data)
        return success(data=params)

    def POST(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._post_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)


class InfoHandler(core.Handler):

    _get_handler_fields = [
        Field('id', T_INT, False),
        Field('token', T_STR, False),
    ]

    def _get_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _get_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        params.pop("token")
        train_id = params.get('id')
        ret = tools.train_info(train_id)
        if ret:
            return success(data=ret)
        return error(UAURET.DATAERR)

    def GET(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._get_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)


class ListHandler(core.Handler):

    _get_handler_fields = [
        Field('size', T_INT, False),
        Field('page', T_INT, False),
        Field('userid', T_INT, True),
        Field('token', T_STR, False),
    ]

    def _get_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _get_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        result = {}
        params = self.validator.data
        params.pop("token")
        size = params.get('size')
        page = params.get('page')
        userid = params.get('userid')
        offset, limit = tools.gen_offset(page, size)
        ret = tools.train_list(offset, limit, userid)
        total = tools.train_total(userid)
        page_num = int(math.ceil(float(total) / float(size)))
        params['trains'] = ret
        params['page_num'] = page_num
        return success(data=params)

    def GET(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._get_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)


class CompleteHandler(core.Handler):

    _post_handler_fields = [
        Field('id', T_INT, False),
        Field('step', T_INT, False),
        Field('name', T_STR, False),
        Field('item_id', T_INT, False),
        Field('times', T_INT, True),
        Field('token', T_STR, False),
        # Field('result', T_STR, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        params.pop("token")
        train_id = params.get('id')
        step = params.get('step')
        name = params.get('name')
        times = params.get('times')
        item_id = params.get('item_id')

        if not self.req.input().has_key('result'):
            return error(UAURET.PARAMERR)
        result = self.req.input().get('result')
        result = json.loads(result)

        ret = tools.verify_train(train_id)
        if not ret:
            log.debug('func=%s|train_id=%s|invalid', inspect.stack()[0][3], train_id)
            return error(UAURET.DATAERR)

        presc_id = ret.get('presc_id')
        items = [item['item_id'] for item in tools.get_all_presc_item(presc_id)]
        log.debug('func=%s|train_id=%s|items=%s', inspect.stack()[0][3], train_id, items)
        if int(item_id) not in items:
            log.debug('func=%s|item_id=%s|invalid', inspect.stack()[0][3], item_id)
            return error(UAURET.DATAERR)

        flag = tools.check_result(name, result)
        if not flag:
            return error(UAURET.DATAERR)

        flag = tools.train_complete(train_id, step, result, name, presc_id, item_id, times)
        if flag:
            params.pop('times')
            return success(data=params)
        return error(UAURET.DATAERR)

    def POST(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._post_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)


class CloseHandler(core.Handler):

    _post_handler_fields = [
        Field('id', T_INT, False),
        Field('token', T_STR, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        params.pop("token")
        train_id = params.get('id')
        flag = tools.train_close(train_id)
        if not flag:
            return error(UAURET.DATAERR)
        params['state'] = define.UYU_TRAIN_STATE_CLOSE
        return success(data=params)

    def POST(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._post_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)


class QrcodeHandler(core.Handler):

    _get_handler_fields = [
        Field('device_id', T_INT, False),
        Field('token', T_STR, False),
    ]

    def _get_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _get_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        device_id = params.get('device_id')
        qrcode_txt = 'http://baidu.com'
        ret = tools.gen_qrcode_base64(qrcode_txt)
        data = {'device_id': device_id, 'qrcode': qrcode_txt, 'qrcode_pic': ret}
        return success(data=data)

    def GET(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._get_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)
