# -*- coding: utf-8 -*-
import math
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
        Field('name', T_STR, False),
        Field('item_type', T_INT, False, match=r'^([0-1]){1}$'),
        # Field('content', T_STR, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        name = params.get('name')
        item_type = params.get('item_type')
        if not self.req.input().has_key('content'):
            return error(UAURET.PARAMERR)
        content = self.req.input().get('content')
        if not tools.verify_item_type(item_type):
            return error(UAURET.DATAERR)
        ret = tools.item_create(name, item_type, content)
        log.debug('func item_create ret=%d', ret)
        if ret != None:
            item_id = ret
            params.update({'id': item_id})
            return success(data=params)
        return error(UAURET.CREATEITEMERR)


    def POST(self):
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
        Field('name', T_STR, False),
        Field('item_type', T_INT, False, match=r'^([0-1]){1}$'),
        # Field('content', T_STR, False),
    ]

    def _post_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_check_device_session(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _post_handler(self):
        if not self.device.sauth:
            return error(UAURET.SESSIONERR)
        params = self.validator.data
        item_id = params.get('id')
        name = params.get('name')
        item_type = params.get('item_type')
        if not self.req.input().has_key('content'):
            return error(UAURET.PARAMERR)
        content = self.req.input().get('content')
        if not tools.verify_item_type(item_type):
            return error(UAURET.DATAERR)
        ret = tools.item_update(name, item_type, content, item_id)
        if ret:
            return success(data=params)
        return error(UAURET.UPDATEITEMERR)


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
        item_id = params.get('id')
        ret = tools.item_info(item_id)
        if ret:
            return success(data=ret)
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
        ret = tools.item_list(offset, limit)
        total = tools.item_total()
        page_num = int(math.ceil(float(total) / float(size)))
        result['size'] = size
        result['page'] = page
        result['page_num'] = page_num
        result['items'] = ret
        return success(data=result)


    def GET(self):
        try:
            self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
            ret = self._get_handler()
            self.write(ret)
        except Exception as e:
            log.warn(e)
            log.warn(traceback.format_exc())
            return error(UAURET.SERVERERR)
