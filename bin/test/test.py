# -*- coding: utf-8 -*-
import json
import hashlib
import unittest
from zbase.base import logger
from zbase.base.http_client import RequestsClient
from zbase.server.client import HttpClient

log = logger.install('stdout')

class TestUyuInstrument(unittest.TestCase):

    def setUp(self):
        self.url = ''
        self.send = {}
        self.host = '127.0.0.1'
        self.port = 8087
        self.timeout = 2000
        self.server = [{'addr':(self.host, self.port), 'timeout':self.timeout},]
        self.client = HttpClient(self.server, client_class = RequestsClient)
        self.headers = {'cookie': 'token=94d846e1-8de1-4e18-aa2d-176839717e53'}

    @unittest.skip("skipping")
    def test_device_login(self):
        self.url = '/login'
        self.send = {
            "device_addr": "bt_v1",
            "password": 123456
        }
        ret = self.client.get(self.url, self.send)
        log.info(ret)
        print '--headers--'
        print self.client.client.headers
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_item_create(self):
        self.url = '/v1/item/create'
        self.send = {
            "device_addr": "bt_v1",
            "name": '项目6',
            "item_type": 1,
            "content": "test"
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')

    @unittest.skip("skipping")
    def test_item_update(self):
        self.url = '/v1/item/update'
        self.send = {
            "device_addr": "bt_v1",
            "name": '项目7',
            "item_type": 1,
            "content": "test",
            "id": 6,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')

    @unittest.skip("skipping")
    def test_item_info(self):
        self.url = '/v1/item/info'
        self.send = {
            "device_addr": "bt_v1",
            "id": 7,
        }
        ret = self.client.get(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_item_list(self):
        self.url = '/v1/item/list'
        self.send = {
            "device_addr": "bt_v1",
            "size": 10,
            "page": 1,
        }
        ret = self.client.get(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_prescription_create(self):
        self.url = '/v1/prescription/create'
        self.send = {
            "device_addr": "bt_v1",
            "userid": 1276,
            "optometrist_id": 1199,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')

    @unittest.skip("skipping")
    def test_prescription_update(self):
        self.url = '/v1/prescription/update'
        self.send = {
            "device_addr": "bt_v1",
            "id": 1,
            "userid": 1276,
            "optometrist_id": 1207,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_prescription_info(self):
        self.url = '/v1/prescription/info'
        self.send = {
            "device_addr": "bt_v1",
            "id": 1,
        }
        ret = self.client.get(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_prescription_add_item(self):
        self.url = '/v1/prescription/add_item'
        param = {
            "trade_type": 0,
            "eye_type": 1,
            "left_eye_level": "+1.50/-1.50",
            "right_eye_level": "+1.50/-1.50",
            "font_size": 15,
            "line_type": 1,
            "line_count": 2,
            "pic_count": 3,
        }
        param_str = json.dumps(param)
        self.send = {
            "device_addr": "bt_v1",
            "id": 1,
            "item_id": 2,
            "count": 2,
            "train_type": 0,
            "param": param_str
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_prescription_del_item(self):
        self.url = '/v1/prescription/del_item'
        self.send = {
            "device_addr": "bt_v1",
            "id": 1,
            "prescitemid": 1,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')



    # @unittest.skip("skipping")
    def test_prescription_update_item(self):
        self.url = '/v1/prescription/update_item'
        param = {
            "trade_type": 1,
            "eye_type": 1,
            "left_eye_level": "+1.65/-1.50",
            "right_eye_level": "+1.80/-1.50",
            "font_size": 12,
            "line_type": 2,
            "line_count": 2,
            "pic_count": 4,
        }
        param_str = json.dumps(param)
        self.send = {
            "device_addr": "bt_v1",
            "id": 1,
            "prescitemid": 2,
            "count": 2,
            "train_type": 0,
            "param": param_str
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


suite = unittest.TestLoader().loadTestsFromTestCase(TestUyuInstrument)
unittest.TextTestRunner(verbosity=2).run(suite)
