import os
os.environ['IN_MEMORY_DB'] = 'Y'

from datetime import date
from unittest import TestCase
import pandas as pd
from app import app
from services.db import dbs
from tests.utils import create_user_table_from_df, create_record_table_from_df


class TestRecordDeletion(TestCase):
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
        cls.record_df = pd.DataFrame(
            columns=['username', 'date', 'lat', 'lon', 'distance', 'time', 'weather'],
            data=[
                ['tonyfoltz', '2020-09-23', 38.7, 46.2, 9369, 25, 'Clouds'],
                ['jeffreywood', '2020-09-21', -26.2, -82.0, 8251, 10, 'Clear'],
                ['tonyfoltz', '2020-09-22', -8.3, 37.9, 3979, 13, 'Clear'],
                ['tonyfoltz', '2020-09-23', 27.1, 19.9, 8743, 43, 'Rain'],
            ]
        )

        create_user_table_from_df(cls.user_df, cls.admin_token)

    @classmethod
    def tearDownClass(cls):
        dbs.clear_user_table()

    def setUp(self):
        create_record_table_from_df(self.record_df, self.admin_token)

    def tearDown(self):
        dbs.clear_record_table()

    def test_delete_record_unauthenticated(self):
        resp = self.client.delete('/record/3', headers={'content-type': 'application/json', 'Authorization': 'dummy token'})
        self.assertEqual(resp.status_code, 401)

    def test_delete_record_staff_role(self):
        resp = self.client.delete('/record/3', headers={'content-type': 'application/json', 'Authorization': self.staff_token})
        self.assertEqual(resp.status_code, 403)

    def test_delete_record_of_other_people_user_role(self):
        resp = self.client.delete('/record/2', headers={'content-type': 'application/json', 'Authorization': self.user_token})
        self.assertEqual(resp.status_code, 403)

    def test_delete_record_user_role(self):
        resp = self.client.delete('/record/3', headers={'content-type': 'application/json', 'Authorization': self.user_token})
        self.assertEqual(resp.status_code, 200)

        result = dbs.read_records(self.admin_token, {})
        expected = [
            {'date': date(2020, 9, 23), 'distance': 9369, 'lat': 38.7, 'lon': 46.2, 'rid': 1, 'time': 25, 'username': 'tonyfoltz', 'weather': 'Clouds'},
            {'date': date(2020, 9, 21), 'distance': 8251, 'lat': -26.2, 'lon': -82.0, 'rid': 2, 'time': 10, 'username': 'jeffreywood', 'weather': 'Clear'},
            {'date': date(2020, 9, 23), 'distance': 8743, 'lat': 27.1, 'lon': 19.9, 'rid': 4, 'time': 43, 'username': 'tonyfoltz', 'weather': 'Rain'},
        ]
        self.assertEqual(result, expected)

    def test_delete_record_admin_role(self):
        resp = self.client.delete('/record/3', headers={'content-type': 'application/json', 'Authorization': self.admin_token})
        self.assertEqual(resp.status_code, 200)

        result = dbs.read_records(self.admin_token, {})
        expected = [
            {'date': date(2020, 9, 23), 'distance': 9369, 'lat': 38.7, 'lon': 46.2, 'rid': 1, 'time': 25, 'username': 'tonyfoltz', 'weather': 'Clouds'},
            {'date': date(2020, 9, 21), 'distance': 8251, 'lat': -26.2, 'lon': -82.0, 'rid': 2, 'time': 10, 'username': 'jeffreywood', 'weather': 'Clear'},
            {'date': date(2020, 9, 23), 'distance': 8743, 'lat': 27.1, 'lon': 19.9, 'rid': 4, 'time': 43, 'username': 'tonyfoltz', 'weather': 'Rain'},
        ]
        self.assertEqual(result, expected)

