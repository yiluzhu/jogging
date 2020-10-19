import os
os.environ['IN_MEMORY_DB'] = 'Y'

from unittest import TestCase
import pandas as pd
from app import app
from services.db import dbs
from tests.utils import create_user_table_from_df, create_record_table_from_df


class TestReport(TestCase):
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
        cls.record_df = pd.DataFrame(
            columns=['username', 'date', 'lat', 'lon', 'distance', 'time', 'weather'],
            data=[
                ['tonyfoltz', '2020-09-23', 38.7, 46.2, 9369, 25, 'Clouds'],
                ['jeffreywood', '2020-09-21', -26.2, -82.0, 8251, 10, 'Clear'],
                ['jeffreywood', '2020-09-21', 37.8, -145.6, 7572, 7, 'Clouds'],
                ['tonyfoltz', '2020-09-22', -8.3, 37.9, 3979, 13, 'Clear'],
                ['jeffreywood', '2020-09-24', 51.0, -119.8, 5131, 29, 'Rain'],
                ['tonyfoltz',  '2020-09-23', 27.1, 19.9, 8743, 43, 'Clear'],
                ['jeffreywood', '2020-09-24', 13.3, 32.9, 6581, 13, 'Clouds'],
                ['tonyfoltz', '2020-09-22', 19.3, 144.2, 4951, 45, 'Clouds'],
                ['jeffreywood',  '2020-09-25', -46.3, -24.4, 5337, 50, 'Clouds'],
                ['jeffreywood', '2020-09-25', 46.5, -177.4, 3223, 39, 'Rain'],
            ]
        )

        create_user_table_from_df(cls.user_df, cls.admin_token)
        create_record_table_from_df(cls.record_df, cls.admin_token)

    @classmethod
    def tearDownClass(cls):
        dbs.clear_record_table()
        dbs.clear_user_table()

    def test_make_report_unauthenticated(self):
        resp = self.client.get("/report?week_start_date=2020-09-21", headers={'content-type': 'application/json', 'Authorization': 'dummy'})
        self.assertEqual(resp.status_code, 401)

    def test_make_report(self):
        resp = self.client.get("/report?week_start_date=2020-09-21", headers={'content-type': 'application/json', 'Authorization': self.user_token})
        self.assertEqual(resp.status_code, 200)

        expected = {'speed': 214.61904761904762, 'total_distance(meters)': 27042, 'total_time(minutes)': 126}
        self.assertEqual(expected, resp.json['data'])

