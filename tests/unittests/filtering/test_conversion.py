import datetime
from unittest import TestCase
from filtering.conversion import convert_str_to_filters


class TestFilterConversion(TestCase):

    def test_simple_filter(self):
        filter_str = "date == '2016-05-01'"
        result = convert_str_to_filters(filter_str)

        expected = {'field': 'date', 'op': '==', 'value': datetime.date(2016, 5, 1)}
        self.assertEqual(expected, result)

    def test_2_level2_filter(self):
        filter_str = '(distance > 20) or (distance < 10)'
        result = convert_str_to_filters(filter_str)

        expected = {
            'or': [
                {'field': 'distance', 'op': '>', 'value': 20},
                {'field': 'distance', 'op': '<', 'value': 10},
            ]
        }
        self.assertEqual(expected, result)

    def test_3_levels_filter(self):
        filter_str = "(username == 'helenkelly') and ((distance > 2500) or (distance < 1000))"
        result = convert_str_to_filters(filter_str)

        expected = {
            'and': [
                {'field': 'username', 'op': '==', 'value': 'helenkelly'},
                {
                    'or': [
                        {'field': 'distance', 'op': '>', 'value': 2500},
                        {'field': 'distance', 'op': '<', 'value': 1000},
                    ]
                }
            ]
        }
        self.assertEqual(expected, result)
