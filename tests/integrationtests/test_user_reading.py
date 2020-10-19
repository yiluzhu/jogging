import os
os.environ['IN_MEMORY_DB'] = 'Y'

from unittest import TestCase
import pandas as pd
from app import app
from services.db import dbs
from tests.utils import create_user_table_from_df


class TestUserReading(TestCase):
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
                ['antoniasimcox', '7e24', 'Antonia', 'Simcox', 'antonia.simcox@gmail.com', 'user', ''],
            ]
        )

        create_user_table_from_df(cls.user_df, cls.admin_token)

    @classmethod
    def tearDownClass(cls):
        dbs.clear_user_table()

    def test_user_unauthenticated(self):
        resp = self.client.get('/user', headers={'content-type': 'application/json', 'Authorization': 'dummy token'})
        self.assertEqual(resp.status_code, 401)

    def test_user_no_access(self):
        resp = self.client.get('/user', headers={'content-type': 'application/json', 'Authorization': self.user_token})
        self.assertEqual(resp.status_code, 403)

    def test_user_admin_role(self):
        resp = self.client.get('/user', headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 200)

        expected = [
            {'email': 'yilu.zhu@gmail.com', 'forename': 'Yilu', 'surname': 'Zhu', 'username': 'yiluzhu', 'role': 'admin', 'token': self.admin_token},
            {'email': 'alex.zhu@gmail.com', 'forename': 'Alex', 'surname': 'Zhu', 'username': 'alexzhu', 'role': 'staff', 'token': self.staff_token},
            {'email': 'tony.foltz@gmail.com', 'forename': 'Tony', 'surname': 'Foltz', 'username': 'tonyfoltz', 'role': 'user', 'token': self.user_token},
            {'email': 'jeffrey.wood@gmail.com', 'forename': 'Jeffrey', 'surname': 'Wood', 'username': 'jeffreywood', 'role': 'user', 'token': ''},
            {'email': 'antonia.simcox@gmail.com', 'forename': 'Antonia', 'surname': 'Simcox', 'username': 'antoniasimcox', 'role': 'user', 'token': ''},
        ]
        self.assertEqual(expected, resp.json['data'])

    def test_user_staff_role(self):
        resp = self.client.get('/user', headers={'content-type': 'application/json', 'Authorization': self.staff_token})
        self.assertEqual(resp.status_code, 200)

        expected = [
            {'email': 'yilu.zhu@gmail.com', 'forename': 'Yilu', 'surname': 'Zhu', 'username': 'yiluzhu', 'role': 'admin', 'token': self.admin_token},
            {'email': 'alex.zhu@gmail.com', 'forename': 'Alex', 'surname': 'Zhu', 'username': 'alexzhu', 'role': 'staff', 'token': self.staff_token},
            {'email': 'tony.foltz@gmail.com', 'forename': 'Tony', 'surname': 'Foltz', 'username': 'tonyfoltz', 'role': 'user', 'token': self.user_token},
            {'email': 'jeffrey.wood@gmail.com', 'forename': 'Jeffrey', 'surname': 'Wood', 'username': 'jeffreywood', 'role': 'user', 'token': ''},
            {'email': 'antonia.simcox@gmail.com', 'forename': 'Antonia', 'surname': 'Simcox', 'username': 'antoniasimcox', 'role': 'user', 'token': ''},
        ]
        self.assertEqual(expected, resp.json['data'])

    def test_user_paging(self):
        resp = self.client.get('/user?page=2&pagesize=2', headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 200)

        expected = [
            {'email': 'tony.foltz@gmail.com', 'forename': 'Tony', 'surname': 'Foltz', 'username': 'tonyfoltz', 'role': 'user', 'token': self.user_token},
            {'email': 'jeffrey.wood@gmail.com', 'forename': 'Jeffrey', 'surname': 'Wood', 'username': 'jeffreywood', 'role': 'user', 'token': ''},
        ]
        self.assertEqual(expected, resp.json['data'])

    def test_user_simple_filter(self):
        resp = self.client.get("/user?filter=surname == 'Wood'",
                               headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 200)

        expected = [
            {'email': 'jeffrey.wood@gmail.com', 'forename': 'Jeffrey', 'surname': 'Wood', 'username': 'jeffreywood', 'role': 'user', 'token': ''}
        ]
        self.assertEqual(expected, resp.json['data'])

    def test_user_complex_filter(self):
        resp = self.client.get("/user?filter=(forename == 'Tony') or (surname == 'Simcox')",
                               headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 200)

        expected = [
            {'email': 'tony.foltz@gmail.com', 'forename': 'Tony', 'surname': 'Foltz', 'username': 'tonyfoltz', 'role': 'user', 'token': self.user_token},
            {'email': 'antonia.simcox@gmail.com', 'forename': 'Antonia', 'surname': 'Simcox', 'username': 'antoniasimcox', 'role': 'user', 'token': ''},
        ]
        self.assertEqual(expected, resp.json['data'])

    def test_user_invalid_filter(self):
        resp = self.client.get("/user?filter=email==a.b@gmail.com",
                               headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 400)
