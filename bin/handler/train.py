# -*- coding: utf-8 -*-
import math
import json
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
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
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
        channel_id = ret.get('channel_id', None)
        store_id = ret.get('store_id', None)
        if store_id == None or channel_id == None:
            log.warn('device no bind device_id=%s|channel_id=%s|store_id=%s|', device_id, channel_id, store_id)
            return error(UAURET.DEVICEUNBINDERR)
        ret = tools.get_user_presc(userid)
        if not ret:
            return error(UAURET.USERNOPRESCERR)
        presc_id = ret['id']
        train_id = tools.train_create(params, channel_id, store_id, presc_id)
        if train_id is None:
            return error(UAURET.DATAERR)
        params['id'] = train_id
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
    ]

    def _get_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _get_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
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
        Field('page', T_INT, False)
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
        size = params.get('size')
        page = params.get('page')
        offset, limit = tools.gen_offset(page, size)
        ret = tools.train_list(offset, limit)
        total = tools.train_total()
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
        Field('times', T_INT, True),
        Field('result', T_STR, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        train_id = params.get('id')
        step = params.get('step')
        times = params.get('times')
        result = params.get('result')
        flag = tools.train_complete(train_id, step, result, times)
        if flag:
            params.pop('times')
            params.pop('result')
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
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
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
        Field('device_id', T_INT, False)
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
