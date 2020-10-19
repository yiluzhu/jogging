import datetime
from unittest import TestCase
from services.weather import WeatherAPI


class TestWeatherAPI(TestCase):

    def setUp(self):
        self.api = WeatherAPI()

    def test_get_weather_for_today(self):
        date = datetime.datetime.today().date()
        result = self.api.get_weather(date, 50.3, 0.7)  # London

        self.assertTrue(isinstance(result, str))
        self.assertNotIn(result, ('Unknown', ''))

    def test_get_weather_for_10_days_ago(self):
        """Free account in api.openweathermap.org only support history of 5 days
        """
        date = datetime.datetime.today().date() - datetime.timedelta(days=10)
        result = self.api.get_weather(date, 50.3, 0.7)  # London

        self.assertEqual(result, 'Unknown')
