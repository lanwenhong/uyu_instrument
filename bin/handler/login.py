# -*- coding: utf-8 -*-
from zbase.web import core
from zbase.web import template
from zbase.web.validator import with_validator_self, Field, T_REG, T_INT, T_STR

from uyubase.base.response import success, error, UAURET
from uyubase.uyu import define
from zbase.base.dbpool import with_database
from uyubase.uyu.define import UYU_OP_ERR
from uyubase.base.dsession import uyu_set_device_cookie, DSession
from uyubase.base.uyu_device import UDevice
from runtime import g_rt
from config import cookie_conf

import logging, datetime, time

log = logging.getLogger()

class LoginHandler(core.Handler):

    _get_handler_fields = [
        Field('password', T_STR, False),
        Field('device_addr', T_STR, False),
    ]

    def _get_handler_errfunc(self, msg):
        return error(UAURET.PARAMERR, respmsg=msg)

    @uyu_set_device_cookie(g_rt.redis_pool, cookie_conf)
    @with_validator_self
    def _get_handler(self, *args):
        params = self.validator.data
        device_addr = params['device_addr']
        password = params["password"]
        d_op = UDevice()
        ret = d_op.call('check_device_login', device_addr, password)
        if not d_op.login or ret == UYU_OP_ERR:
            log.warn('device_addr: %s login forbidden', device_addr)
            return error(UAURET.USERERR)

        log.debug("get device data: %s", d_op.data)
        log.debug("device_addr: %s login success", d_op.data['device_addr'])
        return success({"device_addr": d_op.data['device_addr'], "token": self.session.sk})


    def GET(self, *args):
        self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
        ret = self._get_handler(args)
        return ret
