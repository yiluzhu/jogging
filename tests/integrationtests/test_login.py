import os
os.environ['IN_MEMORY_DB'] = 'Y'

import json
from unittest import TestCase
import pandas as pd
from app import app
from services.db import dbs
from tests.utils import create_user_table_from_df


class TestLogin(TestCase):
    @classmethod
    def setUpClass(cls):
        app.testing = True
        cls.client = app.test_client()

        cls.admin_token = 'a2258791-5dee-4cf7-a84c-56f35bdf1bc7'
        cls.user_token = '762b3b20-e7e3-4590-ae5a-a2abee69f50e'

        cls.user_df = pd.DataFrame(
            columns=['username', 'password', 'forename', 'surname', 'email', 'role', 'token'],
            data=[
                ['yiluzhu', '4a0c', 'Yilu', 'Zhu', 'yilu.zhu@gmail.com', 'admin', cls.admin_token],
                ['tonyfoltz', '7e24', 'Tony', 'Foltz', 'tony.foltz@gmail.com', 'user', cls.user_token],
                ['jeffreywood', 'abc123', 'Jeffrey', 'Wood', 'jeffrey.wood@gmail.com', 'user', ''],
            ]
        )

    def setUp(self):
        create_user_table_from_df(self.user_df, self.admin_token)

    def tearDown(self):
        dbs.clear_user_table()

    def test_heartbeat(self):
        resp = self.client.get('/heartbeat', headers={'content-type': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, b'OK')

    def test_login_wrong_username(self):
        params = {
            'username': 'jw',
            'password': 'abc123'
        }
        resp = self.client.post('/login', data=json.dumps(params), headers={'content-type': 'application/json'})
        self.assertEqual(resp.status_code, 401)

    def test_login_wrong_password(self):
        params = {
            'username': 'jeffreywood',
            'password': '123456'
        }
        resp = self.client.post('/login', data=json.dumps(params), headers={'content-type': 'application/json'})
        self.assertEqual(resp.status_code, 401)

    def test_login_successful(self):
        params = {
            'username': 'jeffreywood',
            'password': 'abc123'
        }
        resp = self.client.post('/login', data=json.dumps(params), headers={'content-type': 'application/json'})
        self.assertEqual(resp.status_code, 200)

        token = resp.json['token']
        self.assertEqual(len(token), 36)
        self.assertTrue(isinstance(token, str))

        result = dbs.read_user_info(self.admin_token, {})
        expected = [
            {'username': 'yiluzhu', 'forename': 'Yilu', 'surname': 'Zhu', 'email': 'yilu.zhu@gmail.com', 'role': 'admin', 'token': self.admin_token},
            {'username': 'tonyfoltz', 'forename': 'Tony', 'surname': 'Foltz', 'email': 'tony.foltz@gmail.com', 'role': 'user', 'token': self.user_token},
            {'username': 'jeffreywood', 'forename': 'Jeffrey', 'surname': 'Wood', 'email': 'jeffrey.wood@gmail.com', 'role': 'user', 'token': token}
        ]
        self.assertEqual(result, expected)

    def test_logout(self):
        resp = self.client.get('/logout', headers={'content-type': 'application/json', 'Authorization': self.user_token})
        self.assertEqual(resp.status_code, 200)

        result = dbs.read_user_info(self.admin_token, {})
        expected = [
            {'username': 'yiluzhu', 'forename': 'Yilu', 'surname': 'Zhu', 'email': 'yilu.zhu@gmail.com', 'role': 'admin', 'token': self.admin_token},
            {'username': 'tonyfoltz', 'forename': 'Tony', 'surname': 'Foltz', 'email': 'tony.foltz@gmail.com', 'role': 'user', 'token': ''},
            {'username': 'jeffreywood', 'forename': 'Jeffrey', 'surname': 'Wood', 'email': 'jeffrey.wood@gmail.com', 'role': 'user', 'token': ''}
        ]
        self.assertEqual(result, expected)
