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
        Field('optometrist_id', T_INT, False),
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
        optometrist_id = params.get('optometrist_id')
        flag = tools.verify_user(userid=userid)
        if not flag:
            return error(UAURET.USERNOTEXISTS)
        flag = tools.verify_user(optometrist_id, define.UYU_USER_ROLE_EYESIGHT)
        if not flag:
            return error(UAURET.USERNOTEXISTS)
        prescription_id = tools.prescription_create(userid, optometrist_id)
        if prescription_id is None:
            return error(UAURET.CREATEPRESCRIPTIONERR)
        params.update({'id': prescription_id})
        return success(data=params)

    def POST(self, *args):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._post_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)


class UpdateHandler(core.Handler):

    _post_handler_fields = [
        Field('id', T_INT, False),
        Field('userid', T_INT, False),
        Field('optometrist_id', T_INT, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        prescription_id = params.get('id')
        userid = params.get('userid')
        optometrist_id = params.get('optometrist_id')
        flag = tools.verify_user(userid=userid)
        if not flag:
            return error(UAURET.USERNOTEXISTS)
        flag = tools.verify_user(optometrist_id, define.UYU_USER_ROLE_EYESIGHT)
        if not flag:
            return error(UAURET.USERNOTEXISTS)
        ret = tools.prescription_update(prescription_id, userid, optometrist_id)
        if not ret:
            return error(UAURET.UPDATEPRESCRIPTIONERR)
        return success(data=params)

    def POST(self, *args):
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
        Field('id', T_INT, False)
    ]

    def _get_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _get_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        prescription_id = params.get('id')
        presc_info, items = tools.prescription_info(prescription_id)
        if presc_info:
            presc_info['items'] = items
            return success(data=presc_info)
        else:
            return error(UAURET.NODATA)

    def GET(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._get_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)


class AddItemHandler(core.Handler):

    _post_handler_fields = [
        Field('id', T_INT, False),
        Field('item_id', T_INT, False),
        Field('count', T_INT, False),
        Field('train_type', T_INT, False, match=r'^([0-2]){1}$'),
        # Field('param', T_STR, False), # validator 解析带逗号的字符串出错
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        prescription_id = params.get('id')
        item_id = params.get('item_id')
        count = params.get('count')
        train_type = params.get('train_type')
        if not self.req.input().has_key('param'):
            return error(UAURET.PARAMERR)

        param_str = self.req.input().get('param')
        param = json.loads(param_str)

        ret = tools.verify_presc(prescription_id)
        if not ret:
            return error(UAURET.NODATA)
        userid = ret.get('userid')
        ret = tools.verify_item(item_id)
        if not ret:
            return error(UAURET.NODATA)

        ret = tools.verify_param(param)
        if not ret:
            return error(UAURET.DATAERR)

        presc_item_id = tools.prescription_add_item(prescription_id, userid, item_id, count, train_type, param_str)

        if ret is None:
            return error()

        params['prescitemid'] = presc_item_id
        params['param'] = param
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


class DelItemHandler(core.Handler):

    _post_handler_fields = [
        Field('id', T_INT, False),
        Field('prescitemid', T_INT, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        presc_id = params.get('id')
        presc_item_id = params.get('prescitemid')
        flag = tools.prescription_del_item(presc_id, presc_item_id)
        if flag:
            return success(data=params)
        else:
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


class UpdateItemHandler(core.Handler):

    _post_handler_fields = [
        Field('id', T_INT, False),
        Field('prescitemid', T_INT, False),
        Field('count', T_INT, False),
        Field('train_type', T_INT, False, match=r'^([0-2]){1}$'),
        # Field('param', T_STR, False), # validator 解析带逗号的字符串出错
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        prescription_id = params.get('id')
        presc_item_id = params.get('prescitemid')
        count = params.get('count')
        train_type = params.get('train_type')
        if not self.req.input().has_key('param'):
            return error(UAURET.PARAMERR)

        param_str = self.req.input().get('param')
        param = json.loads(param_str)
        ret = tools.verify_param(param)
        if not ret:
            return error(UAURET.DATAERR)
        flag = tools.prescription_update_item(prescription_id, presc_item_id, count, train_type, param_str)
        if flag:
            presc_item_info = tools.verify_presc_item(presc_item_id)
            item_id = presc_item_info.get('item_id')
            params['item_id'] = item_id
            params['param'] = param
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
