import datetime
import requests
from loguru import logger


class WeatherAPI:
    """Request weather data from open weather: api.openweathermap.org"""

    APPID = ''
    URL = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'

    def http_get(self, params):
        params['appid'] = self.APPID
        resp = requests.get(self.URL,
                            headers={"Content-Type": "application/json"},
                            params=params)
        if resp.status_code == 200:
            data = resp.json()
            return data
        else:
            msg = f'ERROR: {resp.status_code}: {resp.text}'
            logger.error(msg)

    def get_weather(self, date, lat, lon):
        dt = round(datetime.datetime.combine(date, datetime.datetime.min.time()).timestamp())
        data = self.http_get({'dt': dt, 'lon': lon, 'lat': lat})
        if data:
            return data['current']['weather'][0]['main']
        else:
            return 'Unknown'
