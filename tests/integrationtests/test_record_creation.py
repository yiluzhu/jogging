import os
os.environ['IN_MEMORY_DB'] = 'Y'

import json
from datetime import date, timedelta
from unittest import TestCase
from unittest.mock import ANY
import pandas as pd
from app import app
from services.db import dbs
from tests.utils import create_user_table_from_df


class TestRecordCreation(TestCase):
    @classmethod
    def setUpClass(cls):
        app.testing = True
        cls.client = app.test_client()

        cls.admin_token = 'a2258791-5dee-4cf7-a84c-56f35bdf1bc7'
        cls.staff_token = 'f7462ade-e762-40d8-8bce-1dfa47ad1fff'
        cls.user_token = '762b3b20-e7e3-4590-ae5a-a2abee69f50e'

        cls.user_df = pd.DataFrame(
            columns=['username', 'password', 'forename', 'surname', 'email', 'role', 'token'],
            data=[
                ['yiluzhu', '4a0c', 'Yilu', 'Zhu', 'yilu.zhu@gmail.com', 'admin', cls.admin_token],
                ['alexzhu', 'c612', 'Alex', 'Zhu', 'alex.zhu@gmail.com', 'staff', cls.staff_token],
                ['tonyfoltz', '7e24', 'Tony', 'Foltz', 'tony.foltz@gmail.com', 'user', cls.user_token],
            ]
        )
        cls.yesterday = date.today() - timedelta(days=1)
        cls.params = {'username': 'tonyfoltz', 'date': str(cls.yesterday), 'lat': 38.7, 'lon': 46.2, 'distance': 9000, 'time': 25}

        create_user_table_from_df(cls.user_df, cls.admin_token)

    @classmethod
    def tearDownClass(cls):
        dbs.clear_user_table()

    def tearDown(self):
        dbs.clear_record_table()

    def test_create_record_unauthenticated(self):
        resp = self.client.put('/record', data=json.dumps(self.params), headers={'content-type': 'application/json', 'Authorization': 'dummy token'})
        self.assertEqual(resp.status_code, 401)

    def test_create_record_staff_role(self):
        resp = self.client.put('/record', data=json.dumps(self.params), headers={'content-type': 'application/json', 'Authorization': self.staff_token})
        self.assertEqual(resp.status_code, 403)

    def test_create_record_for_unknown_user(self):
        params = {'username': 'unknown', 'date': '2020-09-20', 'lat': 38.7, 'lon': 46.2, 'distance': 9000, 'time': 25}
        resp = self.client.put('/record', data=json.dumps(params), headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 409)

    def test_create_record_user_role(self):
        resp = self.client.put('/record', data=json.dumps(self.params), headers={'content-type': 'application/json', 'Authorization': self.user_token})
        self.assertEqual(resp.status_code, 200)

        result = dbs.read_records(self.admin_token, {})
        expected = [
            {'date': self.yesterday, 'distance': 9000, 'lat': 38.7, 'lon': 46.2, 'rid': 1, 'time': 25, 'username': 'tonyfoltz', 'weather': ANY},
        ]
        self.assertEqual(result, expected)

    def test_create_record_admin_role(self):
        resp = self.client.put('/record', data=json.dumps(self.params), headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 200)

        result = dbs.read_records(self.admin_token, {})
        expected = [
            {'date': self.yesterday, 'distance': 9000, 'lat': 38.7, 'lon': 46.2, 'rid': 1, 'time': 25, 'username': 'tonyfoltz', 'weather': ANY},
        ]
        self.assertEqual(result, expected)
