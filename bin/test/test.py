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
        self.port = 8088
        self.timeout = 2000
        self.server = [{'addr':(self.host, self.port), 'timeout':self.timeout},]
        self.client = HttpClient(self.server, client_class = RequestsClient)
        self.headers = {'cookie': 'token=d5872ece-433f-451c-b4cf-fca97f759489'}

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
            "name": '项目9',
            "item_type": 1,
            "content": param_str
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')

    @unittest.skip("skipping")
    def test_item_update(self):
        self.url = '/v1/item/update'
        self.send = {
            "name": '项目7',
            "item_type": 2,
            "content": "test.20170626_3",
            "id": 7,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')

    @unittest.skip("skipping")
    def test_item_info(self):
        self.url = '/v1/item/info'
        self.send = {
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
            "size": 5,
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
            "userid": 1267,
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
            "id": 5,
            "userid": 1267,
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
            "id": 1,
        }
        ret = self.client.get(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_prescription_add_item(self):
        self.url = '/v1/prescription/add_item'
        self.send = {
            "id": 5,
            "item_id": 2,
            "count": 2,
            "train_type": 0,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_prescription_del_item(self):
        self.url = '/v1/prescription/del_item'
        self.send = {
            "id": 5,
            "presc_item_id": 3,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')



    @unittest.skip("skipping")
    def test_prescription_update_item(self):
        self.url = '/v1/prescription/update_item'
        self.send = {
            "id": 5,
            "presc_item_id": 3,
            "count": 8,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')



    @unittest.skip("skipping")
    def test_train_create(self):
        self.url = '/v1/train/create'
        self.send = {
            "userid": 1276,
            "device_id": 111,
            "item_type": 2,
            "lng": 14.123,
            "lat": 15.234
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_train_info(self):
        self.url = '/v1/train/info'
        self.send = {
            "id": 3,
        }
        ret = self.client.get(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_train_list(self):
        self.url = '/v1/train/list'
        self.send = {
            "size": 10,
            "page": 1,
            "userid": 1276,
        }
        ret = self.client.get(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_train_complete(self):
        self.url = '/v1/train/complete'
        result = {
            "seq": 
                [
                    {
                        "font_size": 10,
                        "eye": "l",
                        "optic": 250,
                        "vision": 0.8
                    }, 
                    {
                        "font_size": 12,
                        "eye": "r",
                        "optic": 250,
                        "vision": 0.8
                    }
                ], 
            "glasses": 'true'
        }
        self.send = {
            "step": 3,
            "times": 40,
            "result": json.dumps(result),
            "name": '视力检查',
            "item_id": 1,
            "id": 3,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    @unittest.skip("skipping")
    def test_train_close(self):
        self.url = '/v1/train/close'
        self.send = {
            "id": 1,
        }
        ret = self.client.post(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')


    # @unittest.skip("skipping")
    def test_train_qrcode(self):
        self.url = '/v1/train/qrcode'
        self.send = {
            "device_id": 1,
        }
        ret = self.client.get(self.url, self.send, headers=self.headers)
        log.info(ret)
        respcd = json.loads(ret).get('respcd')
        self.assertEqual(respcd, '0000')



suite = unittest.TestLoader().loadTestsFromTestCase(TestUyuInstrument)
unittest.TextTestRunner(verbosity=2).run(suite)
