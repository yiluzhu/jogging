import os
os.environ['IN_MEMORY_DB'] = 'Y'

from unittest import TestCase
import pandas as pd
from app import app
from services.db import dbs
from tests.utils import create_user_table_from_df


class TestUserDeletion(TestCase):
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
                ['jeffreywood', '7e24', 'Jeffrey', 'Wood', 'jeffrey.wood@gmail.com', 'user', ''],
            ]
        )

    def setUp(self):
        create_user_table_from_df(self.user_df, self.admin_token)

    def tearDown(self):
        dbs.clear_user_table()

    def test_delete_user_unauthenticated(self):
        resp = self.client.delete('/user/tonyfoltz', headers={'content-type': 'application/json', 'Authorization': 'dummy token'})
        self.assertEqual(resp.status_code, 401)

    def test_delete_user_no_access(self):
        resp = self.client.delete('/user/tonyfoltz', headers={'content-type': 'application/json', 'Authorization': self.user_token})
        self.assertEqual(resp.status_code, 403)

    def test_delete_user_that_has_record(self):
        params = {'username': 'tonyfoltz', 'date': '2020-09-29', 'lat': 38.7, 'lon': 46.2, 'distance': 9000, 'time': 25, 'weather': 'Sunny'}
        dbs.create_a_record(params, self.admin_token)

        resp = self.client.delete('/user/tonyfoltz', headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 409)

        dbs.clear_record_table()

    def test_delete_user_admin_role(self):
        resp = self.client.delete('/user/tonyfoltz', headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 200)

        result = dbs.read_user_info(self.admin_token, {})
        expected = [
            {'email': 'yilu.zhu@gmail.com', 'forename': 'Yilu', 'surname': 'Zhu', 'username': 'yiluzhu', 'role': 'admin', 'token': self.admin_token},
            {'email': 'alex.zhu@gmail.com', 'forename': 'Alex', 'surname': 'Zhu', 'username': 'alexzhu', 'role': 'staff', 'token': self.staff_token},
            {'email': 'jeffrey.wood@gmail.com', 'forename': 'Jeffrey', 'surname': 'Wood', 'username': 'jeffreywood', 'role': 'user', 'token': ''},
        ]
        self.assertEqual(result, expected)

    def test_delete_user_staff_role(self):
        resp = self.client.delete('/user/tonyfoltz', headers={'content-type': 'application/json', 'Authorization': self.staff_token})
        self.assertEqual(resp.status_code, 200)

        result = dbs.read_user_info(self.admin_token, {})
        expected = [
            {'email': 'yilu.zhu@gmail.com', 'forename': 'Yilu', 'surname': 'Zhu', 'username': 'yiluzhu', 'role': 'admin', 'token': self.admin_token},
            {'email': 'alex.zhu@gmail.com', 'forename': 'Alex', 'surname': 'Zhu', 'username': 'alexzhu', 'role': 'staff', 'token': self.staff_token},
            {'email': 'jeffrey.wood@gmail.com', 'forename': 'Jeffrey', 'surname': 'Wood', 'username': 'jeffreywood', 'role': 'user', 'token': ''},
        ]
        self.assertEqual(result, expected)
